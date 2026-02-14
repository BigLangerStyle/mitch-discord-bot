"""
Mitch Discord Bot - Main Bot Module

Handles Discord connection, event handling, and message responses.
Uses Ollama AI integration for natural gaming buddy personality.
Version 1.1.0: Full conversational AI with context tracking
"""

import discord
from discord.ext import commands
import asyncio
import signal
import sys
import time
from collections import defaultdict, deque
from config_loader import load_config
from logger import setup_logging, get_logger
from ollama_client import OllamaClient
from personality import PersonalitySystem
from game_tracker import GameTracker
from suggestion_engine import SuggestionEngine
from player_count import extract_player_count, should_ask_for_count, get_clarification_message

# Load configuration first
config = load_config()

# Setup logging from config
setup_logging(
    log_file=config['logging']['file'],
    log_level=config['logging']['level'],
    max_bytes=config['logging']['max_bytes'],
    backup_count=config['logging']['backup_count']
)

# Get logger for this module
logger = get_logger(__name__)

# Initialize Ollama client
ollama_config = config.get('ollama', {})
ollama_client = OllamaClient(
    host=ollama_config.get('host', 'http://localhost:11434'),
    model=ollama_config.get('model', 'phi3:mini'),
    timeout=ollama_config.get('timeout', 60),
    temperature=ollama_config.get('temperature', 0.8),
    max_tokens=ollama_config.get('max_tokens', 300)
)

# Initialize personality system
personality = PersonalitySystem(ollama_client)

# Discord intents configuration
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.guilds = True
intents.guild_messages = True
intents.members = True  # Required to see server members

# Create bot client
bot = commands.Bot(command_prefix='!', intents=intents)


class MitchBot:
    """Main bot class handling Discord events and responses."""
    
    def __init__(self):
        self.bot = bot
        self.config = config
        self.personality = personality
        self.shutdown_event = asyncio.Event()
        
        # Initialize game tracker
        self.game_tracker = GameTracker(
            db_path=config.get('database', {}).get('path', 'data/mitch.db'),
            config=config
        )
        
        # Initialize suggestion engine
        self.suggestion_engine = SuggestionEngine(
            game_tracker=self.game_tracker,
            personality=personality,
            config=config
        )
        
        # Conversation context tracking (v1.1.0)
        # Maps channel_id -> deque of recent messages
        # Format: {"author": "Username", "content": "message text"}
        conversation_config = config.get('conversation', {})
        self.context_size = conversation_config.get('context_messages', 5)
        self.conversation_history = defaultdict(lambda: deque(maxlen=self.context_size))
        
        # Rate limiting (v1.1.0)
        # Maps user_id -> timestamp of last interaction
        rate_limit_config = config.get('rate_limiting', {})
        self.rate_limit_enabled = rate_limit_config.get('enabled', False)
        self.rate_limit_cooldown = rate_limit_config.get('cooldown_seconds', 5)
        self.rate_limit_message = rate_limit_config.get('message', 'whoa slow down a sec!')
        self.last_interaction = {}
        
        logger.info("MitchBot v1.1.0 initialized with conversation tracking")
        logger.info(f"Context tracking: {self.context_size} messages per channel")
        logger.info(f"Rate limiting: {'enabled' if self.rate_limit_enabled else 'disabled'}")
        
    async def setup(self):
        """Setup bot event handlers."""
        
        @self.bot.event
        async def on_ready():
            """Called when bot successfully connects to Discord."""
            logger.info(f"Mitch connected as {self.bot.user}")
            logger.info(f"Ready to help {len(self.bot.guilds)} servers")
            
            # Set bot status
            activity = discord.Game(name="games with the crew")
            await self.bot.change_presence(activity=activity)
            
        @self.bot.event
        async def on_message(message):
            """Handle incoming messages and respond to mentions."""
            
            # Ignore messages from the bot itself
            if message.author == self.bot.user:
                return
            
            # Track message in conversation history (v1.1.0)
            # Only track messages in channels where bot is mentioned
            # This keeps memory usage low
            if self.bot.user in message.mentions or len(self.conversation_history.get(message.channel.id, [])) > 0:
                self._add_to_context(message)
            
            # Check if bot was mentioned
            if self.bot.user in message.mentions:
                await self._handle_mention(message)
            
            # Process commands (for future use)
            await self.bot.process_commands(message)
    
    def _add_to_context(self, message):
        """
        Add message to conversation context.
        
        Args:
            message: Discord message object
        """
        # Format: simple author + content for context
        context_entry = {
            "author": message.author.display_name,
            "content": message.content.replace(f'<@{self.bot.user.id}>', 'Mitch').strip()
        }
        
        self.conversation_history[message.channel.id].append(context_entry)
        
    def _get_conversation_context(self, channel_id) -> list:
        """
        Get recent conversation context for a channel.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            List of recent messages (oldest to newest)
        """
        return list(self.conversation_history.get(channel_id, []))
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user is rate limited.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            True if rate limited (too fast), False if OK
        """
        if not self.rate_limit_enabled:
            return False
        
        now = time.time()
        last_time = self.last_interaction.get(user_id, 0)
        
        if now - last_time < self.rate_limit_cooldown:
            return True
        
        # Update last interaction time
        self.last_interaction[user_id] = now
        return False
    
    async def _handle_mention(self, message):
        """
        Handle when bot is mentioned in a message.
        
        Detects if user wants game suggestions and routes to suggestion engine,
        or uses general AI conversation for casual messages.
        
        Args:
            message: Discord message object
        """
        try:
            # Check rate limiting (v1.1.0)
            if self._check_rate_limit(message.author.id):
                logger.info(f"Rate limited user {message.author.name}")
                await message.channel.send(self.rate_limit_message)
                return
            
            # Log the mention
            logger.info(
                f"Mitch mentioned by {message.author} in #{message.channel.name}: "
                f"{message.content[:100]}"
            )
            
            # Check if user is asking for game suggestions
            # More flexible keyword matching for natural language
            content_lower = message.content.lower()
            
            # Check if asking for game suggestion (flexible matching)
            asking_for_game = (
                # "what ... game/play" (matches: what game, what should we play, what could we play, etc.)
                ('what' in content_lower and ('play' in content_lower or 'game' in content_lower)) or
                
                # "suggest/recommend ... game"
                (('suggest' in content_lower or 'recommend' in content_lower) and 'game' in content_lower) or
                
                # "give me ... game/suggestion"
                ('give me' in content_lower and ('game' in content_lower or 'suggestion' in content_lower)) or
                
                # Direct requests
                'game suggestion' in content_lower or
                'pick a game' in content_lower or
                'choose a game' in content_lower or
                'any suggestions' in content_lower or
                'any suggestion' in content_lower
            )
            
            # Show typing indicator while processing
            async with message.channel.typing():
                # Small delay to feel more natural
                await asyncio.sleep(0.5)
                
                if asking_for_game:
                    logger.info(f"✓ Detected game suggestion request: '{message.content}'")
                    
                    # Extract explicit player count from message
                    extracted_count = extract_player_count(message.content)
                    
                    # Count online members for fallback/clarification logic
                    try:
                        online_members = [
                            m for m in message.guild.members 
                            if m.status != discord.Status.offline and not m.bot
                        ]
                        online_count = len(online_members)
                    except Exception:
                        online_count = 4  # Safe default
                    
                    # Decide if we need to ask for clarification
                    should_ask, player_count = should_ask_for_count(extracted_count, online_count)
                    
                    if should_ask:
                        # Send clarification question instead of suggesting
                        clarification = get_clarification_message(online_count)
                        logger.info(f"Asking for clarification: {online_count} online, no explicit count")
                        await message.channel.send(clarification)
                        return
                    
                    # We have a clear player count - generate suggestion
                    logger.info(f"Generating suggestion for {player_count} players")
                    start_time = asyncio.get_event_loop().time()
                    
                    # Generate suggestion using suggestion engine
                    response = await self.suggestion_engine.suggest_games(
                        player_count=player_count,
                        requester_name=message.author.name
                    )
                    
                    elapsed = asyncio.get_event_loop().time() - start_time
                    logger.info(f"Suggestion generated ({elapsed:.1f}s)")
                    
                else:
                    # v1.1.0: Casual conversation with context
                    logger.info(f"Handling as casual conversation: '{message.content}'")
                    start_time = asyncio.get_event_loop().time()
                    
                    # Get conversation context
                    context = self._get_conversation_context(message.channel.id)
                    
                    # Generate conversational response with context
                    response = await self.personality.casual_response(
                        message.content,
                        requester_name=message.author.display_name,
                        conversation_history=context
                    )
                    
                    elapsed = asyncio.get_event_loop().time() - start_time
                    logger.info(f"AI response received ({elapsed:.1f}s)")
                
                # Send response
                await message.channel.send(response)
                
                logger.info(f"Response sent: {response[:100]}")
                
        except discord.HTTPException as e:
            logger.error(f"Failed to send message: {e}")
        except Exception as e:
            logger.error(f"Error handling mention: {e}", exc_info=True)
            # Try to send fallback response
            try:
                fallback = self.personality._get_fallback_response()
                await message.channel.send(fallback)
                logger.info(f"Sent fallback response: {fallback}")
            except Exception:
                logger.error("Failed to send fallback response")
    
    def _estimate_player_count(self, message) -> int:
        """
        Estimate player count from message content and server context.
        
        First tries to extract explicit player count from message (e.g., "5 of us").
        If no explicit count, uses online member count as fallback.
        
        Args:
            message: Discord message object
            
        Returns:
            int: Estimated player count (default to 4 if uncertain)
        """
        try:
            # First, try to extract explicit player count from message
            extracted_count = extract_player_count(message.content)
            
            if extracted_count is not None:
                logger.info(f"✓ Extracted explicit player count: {extracted_count}")
                # Clamp to reasonable range
                if extracted_count > 10:
                    logger.info(f"Clamping {extracted_count} to max of 10 players")
                    return 10
                return extracted_count
            
            # No explicit count - count online members (excluding bots)
            online_members = [
                m for m in message.guild.members 
                if m.status != discord.Status.offline and not m.bot
            ]
            count = len(online_members)
            
            # Clamp to reasonable range
            if count < 1:
                count = 4  # Default fallback
            elif count > 10:
                count = 10  # Cap at max game size
                
            logger.info(
                f"Using online member count: {count} players from "
                f"{len(online_members)} online members"
            )
            return count
            
        except Exception as e:
            logger.warning(f"Failed to estimate player count: {e}")
            return 4  # Safe default
    
    async def start(self):
        """Start the bot with error handling."""
        try:
            token = self.config['discord']['token']
            
            if not token or token == 'YOUR_DISCORD_BOT_TOKEN_HERE':
                logger.error(
                    "Discord token not configured. "
                    "Please update config/config.yaml with your bot token."
                )
                sys.exit(1)
            
            logger.info("Starting Mitch Discord Bot v1.1.0...")
            await self.bot.start(token)
            
        except discord.LoginFailure:
            logger.error("Failed to login - invalid Discord token")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to start bot: {e}", exc_info=True)
            sys.exit(1)
    
    async def stop(self):
        """Gracefully stop the bot."""
        logger.info("Shutting down Mitch Bot...")
        await self.bot.close()
        logger.info("Bot shutdown complete")


async def main():
    """Main entry point with graceful shutdown handling."""
    
    mitch = MitchBot()
    await mitch.setup()
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler(sig, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        loop.create_task(mitch.stop())
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await mitch.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        await mitch.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
