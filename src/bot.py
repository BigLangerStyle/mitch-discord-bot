"""
Mitch Discord Bot - Main Bot Module

Handles Discord connection, event handling, and message responses.
Currently uses hardcoded responses (AI integration coming in v0.3.0).
"""

import discord
from discord.ext import commands
import asyncio
import signal
import sys
import random
from config_loader import load_config
from logger import setup_logging, get_logger

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

# Discord intents configuration
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.guilds = True
intents.guild_messages = True
intents.members = True  # Required to see server members

# Create bot client
bot = commands.Bot(command_prefix='!', intents=intents)

# Hardcoded casual responses (AI comes in v0.3.0)
CASUAL_RESPONSES = [
    "yo what's up?",
    "hmm not sure yet, still setting up my game library",
    "I'll have suggestions for you soon, just getting the hang of things",
    "hey! still learning the ropes here",
    "sup? still getting my bearings with the game collection",
]


class MitchBot:
    """Main bot class handling Discord events and responses."""
    
    def __init__(self):
        self.bot = bot
        self.config = config
        self.shutdown_event = asyncio.Event()
        
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
            
            # Check if bot was mentioned
            if self.bot.user in message.mentions:
                await self._handle_mention(message)
            
            # Process commands (for future use)
            await self.bot.process_commands(message)
    
    async def _handle_mention(self, message):
        """
        Handle when bot is mentioned in a message.
        
        Args:
            message: Discord message object
        """
        try:
            # Log the mention
            logger.info(
                f"Mentioned by {message.author} in #{message.channel.name}: "
                f"{message.content[:100]}"
            )
            
            # Show typing indicator
            async with message.channel.typing():
                # Small delay to feel more natural
                await asyncio.sleep(0.5)
                
                # Pick a random casual response
                response = random.choice(CASUAL_RESPONSES)
                
                # Send response
                await message.channel.send(response)
                
                logger.info(f"Responded with: {response}")
                
        except discord.HTTPException as e:
            logger.error(f"Failed to send message: {e}")
        except Exception as e:
            logger.error(f"Error handling mention: {e}", exc_info=True)
    
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
            
            logger.info("Starting Mitch Discord Bot...")
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
