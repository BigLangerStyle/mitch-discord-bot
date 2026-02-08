"""
Mitch's personality system and response generation.

Defines Mitch's character as a casual gaming buddy and handles
AI response generation with appropriate polishing.
"""

import logging
import random
import re
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# System prompt defining Mitch's personality
SYSTEM_PROMPT = """You are Mitch, a casual gaming buddy for a small Discord friend group. Your job is to help them decide what game to play.

PERSONALITY:
- You're one of the crew, not a corporate assistant
- Keep responses brief (under 500 characters, ideally under 300)
- Use casual gaming language naturally (gg, lol, idk, etc.)
- Be honest when you don't know something
- Don't use excessive emojis (maybe one occasionally, or none)
- Don't apologize excessively or be overly formal

GOOD RESPONSES:
"hmm for 4 people, maybe Deep Rock Galactic? you guys haven't touched that in a while"
"you just played Valheim yesterday lol, how about something different?"
"not sure what the vibe is - competitive or co-op?"

BAD RESPONSES:
"I'd be delighted to assist you with game selection! Based on my analysis..."
"Here are my recommendations: 1. Game A, 2. Game B..."
"I apologize, but I don't have enough information..."

Keep it real, keep it short, keep it helpful."""

# Fallback responses if AI is unavailable
CASUAL_RESPONSES = [
    "yo what's up?",
    "hey, not sure what to suggest yet - still learning what you guys like to play",
    "hmm I'd help but I'm still getting the hang of this",
    "sup, what kind of game are you thinking?",
    "hey! what's the vibe - competitive or chill?"
]

# Corporate phrases to strip from AI responses
CORPORATE_PHRASES = [
    r"I'd be happy to",
    r"I'd be delighted to",
    r"I apologize",
    r"I'm sorry",
    r"However,",
    r"Additionally,",
    r"Furthermore,",
    r"Let me",
    r"Allow me to",
    r"Based on my analysis",
    r"I recommend",
    r"Here are my recommendations",
    r"In conclusion",
    r"To summarize",
]


class PersonalitySystem:
    """Manages Mitch's personality and response generation."""
    
    def __init__(self, ollama_client):
        """
        Initialize personality system.
        
        Args:
            ollama_client: OllamaClient instance for AI generation
        """
        self.ollama = ollama_client
        logger.info("Personality system initialized")
    
    async def generate_response(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response to user's message using AI.
        
        Args:
            user_message: The message from the user
            context: Optional context dict (player_count, recent_games, etc.)
                    Reserved for future use - currently unused
                    
        Returns:
            Polished response text ready to send
        """
        # Build the full prompt
        # Future: incorporate context here (player counts, game history, etc.)
        full_prompt = self._build_prompt(user_message, context)
        
        try:
            logger.info("Generating AI response...")
            raw_response = await self.ollama.generate(full_prompt)
            
            # Polish the response to keep it casual
            polished = self._polish_response(raw_response)
            
            logger.info(f"Response generated: {len(polished)} chars")
            return polished
            
        except Exception as e:
            logger.warning(f"AI generation failed: {e}, using fallback")
            return self._get_fallback_response()
    
    def _build_prompt(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build the full prompt to send to AI.
        
        Args:
            user_message: The user's message
            context: Optional context information (not yet implemented)
            
        Returns:
            Complete prompt string
        """
        # Start with system prompt
        prompt_parts = [SYSTEM_PROMPT, "", "USER MESSAGE:"]
        
        # Add context if provided (future enhancement)
        if context:
            if "player_count" in context:
                prompt_parts.append(f"Players online: {context['player_count']}")
            if "recent_games" in context:
                games = ", ".join(context["recent_games"])
                prompt_parts.append(f"Recently played: {games}")
            prompt_parts.append("")
        
        # Add the actual user message
        prompt_parts.append(user_message)
        prompt_parts.append("")
        prompt_parts.append("MITCH'S RESPONSE:")
        
        return "\n".join(prompt_parts)
    
    def _polish_response(self, raw_response: str) -> str:
        """
        Polish AI response to keep it casual and brief.
        
        Removes corporate language, excessive punctuation, and ensures
        the response fits Discord's limits and Mitch's personality.
        
        Args:
            raw_response: Raw text from AI
            
        Returns:
            Polished response text
        """
        response = raw_response.strip()
        
        # Remove corporate phrases
        for phrase in CORPORATE_PHRASES:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        # Clean up excessive punctuation
        response = re.sub(r'!{2,}', '!', response)  # Multiple ! to single !
        response = re.sub(r'\?{2,}', '?', response)  # Multiple ? to single ?
        response = re.sub(r'\.{4,}', '...', response)  # Multiple . to ...
        
        # Remove most emojis (keep maybe one if present)
        # Simple approach: if more than 2 emojis, it's probably too many
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        emoji_count = len(re.findall(emoji_pattern, response))
        if emoji_count > 2:
            # Strip all emojis if excessive
            response = re.sub(emoji_pattern, '', response)
        
        # Clean up whitespace
        response = re.sub(r'\n\s*\n', '\n', response)  # Multiple blank lines
        response = re.sub(r'  +', ' ', response)  # Multiple spaces
        response = response.strip()
        
        # Enforce length limits
        # Discord limit is 2000, but we want to keep it brief
        if len(response) > 500:
            # Try to cut at a sentence boundary
            sentences = response[:500].split('.')
            if len(sentences) > 1:
                response = '.'.join(sentences[:-1]) + '.'
            else:
                response = response[:497] + '...'
        
        # If we somehow ended up with empty response after polishing
        if not response or len(response.strip()) < 5:
            logger.warning("Response too short after polishing, using fallback")
            return self._get_fallback_response()
        
        return response
    
    def _get_fallback_response(self) -> str:
        """
        Get a fallback response if AI fails.
        
        Returns:
            Random casual response
        """
        return random.choice(CASUAL_RESPONSES)
