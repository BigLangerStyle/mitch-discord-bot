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

CRITICAL RULES - FOLLOW EXACTLY:
1. Keep responses VERY brief - under 200 characters, ideally under 100
2. Never use multiple sentences unless absolutely necessary
3. Use lowercase and casual language
4. NO emojis at all
5. NO corporate language ("I'd be happy to", "What do you think?", etc.)
6. NO making up game names - if you don't know, say so
7. Be honest when you don't have information
8. Sound like a friend texting, not a customer service bot

GOOD RESPONSES (copy this style):
"yo"
"sup?"
"hmm not sure - co-op or competitive?"
"idk, what's the vibe?"
"lol you guys just played that yesterday"
"maybe something for 4 people?"

BAD RESPONSES (never do this):
"Hey everyone! What's got you feeling lucky today?"
"Alrighty then! How about we get into some action?"
"I'd be happy to help! What do you think? 🎲"
"Let me recommend something for your crew size"

Remember: You're texting a friend, not writing an essay. Keep it SHORT and CASUAL."""

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
    r"However,?",
    r"Additionally,?",
    r"Furthermore,?",
    r"Let me\s+",
    r"Allow me to",
    r"Based on my analysis",
    r"I recommend",
    r"Here are my recommendations",
    r"In conclusion",
    r"To summarize",
    r"Alrighty then!?",
    r"What do you (?:guys|all) think\??",
    r"What's got you",
    r"Ready to",
    r"How about we",
    r"Should be",
    r"Just sayin'?\.?",
    r"I hope",
    r"Sounds? good\??",
]

# Overly enthusiastic phrases to remove
ENTHUSIASM_PHRASES = [
    r"Hey everyone!",
    r"Hey there!",
    r"Alright!",
    r"Perfect!",
    r"Awesome!",
    r"Great!",
    r"Exciting!",
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
        prompt_parts = [SYSTEM_PROMPT]
        
        # Add context if provided (future enhancement)
        if context:
            prompt_parts.append("\nCONTEXT:")
            if "player_count" in context:
                prompt_parts.append(f"Players online: {context['player_count']}")
            if "recent_games" in context:
                games = ", ".join(context["recent_games"])
                prompt_parts.append(f"Recently played: {games}")
        
        # Add the actual user message
        prompt_parts.append(f"\nUSER: {user_message}")
        prompt_parts.append("\nMITCH (respond in under 100 characters, casual, no emojis):")
        
        return "\n".join(prompt_parts)
    
    def _polish_response(self, raw_response: str) -> str:
        """
        Polish AI response to keep it casual and brief.
        
        Aggressively removes corporate language, excessive punctuation,
        emojis, and ensures the response fits Mitch's personality.
        
        Args:
            raw_response: Raw text from AI
            
        Returns:
            Polished response text
        """
        response = raw_response.strip()
        
        # Remove everything after certain markers (AI instruction artifacts)
        response = re.split(r'---+', response)[0]  # Remove anything after "---"
        response = re.split(r'\*\*Instruction', response)[0]  # Remove instruction artifacts
        response = re.split(r'USER:', response, flags=re.IGNORECASE)[0]  # Remove if AI repeats prompt
        
        # Remove all emojis completely
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\u2600-\u26FF\u2700-\u27BF]'
        response = re.sub(emoji_pattern, '', response)
        
        # Remove corporate and enthusiasm phrases
        for phrase in CORPORATE_PHRASES + ENTHUSIASM_PHRASES:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        # Remove common filler words and phrases at the start
        response = re.sub(r'^(?:Well,?|So,?|Hmm,?)\s+', '', response, flags=re.IGNORECASE)
        
        # Clean up excessive punctuation
        response = re.sub(r'!{2,}', '!', response)  # Multiple ! to single !
        response = re.sub(r'\?{2,}', '?', response)  # Multiple ? to single ?
        response = re.sub(r'\.{4,}', '...', response)  # Multiple . to ...
        response = re.sub(r'[!?]{2,}', '?', response)  # Mixed !? to just ?
        
        # Remove trailing punctuation repetition
        response = re.sub(r'([.!?])\1+$', r'\1', response)
        
        # Clean up whitespace
        response = re.sub(r'\n\s*\n', '\n', response)  # Multiple blank lines
        response = re.sub(r'  +', ' ', response)  # Multiple spaces
        response = response.strip()
        
        # If response has multiple sentences, try to keep only the first one or two
        sentences = re.split(r'(?<=[.!?])\s+', response)
        if len(sentences) > 2:
            # Keep first 2 sentences max
            response = ' '.join(sentences[:2])
        
        # Enforce strict length limits
        # Discord limit is 2000, but we want to keep it very brief
        if len(response) > 300:
            # Try to cut at a sentence boundary
            sentences = response[:300].split('.')
            if len(sentences) > 1:
                response = '.'.join(sentences[:-1]) + '.'
            else:
                # Cut at word boundary
                response = response[:297] + '...'
        
        # If response is still too structured/long, simplify it
        # Look for multi-sentence responses and condense
        if len(response) > 150:
            # Try to extract just the core message
            # Look for questions or key phrases
            if '?' in response:
                # Keep just the question
                parts = response.split('?')
                response = parts[0] + '?'
            else:
                # Take first sentence only
                first_sentence = re.split(r'[.!]', response)[0]
                if len(first_sentence) > 20:
                    response = first_sentence
        
        # Lowercase the first letter unless it's "I" or a proper noun
        if response and len(response) > 0:
            if response[0].isupper() and response[0] != 'I' and not response[0:2].isupper():
                response = response[0].lower() + response[1:]
        
        # Remove trailing periods (casual text style)
        if response.endswith('.') and not response.endswith('...'):
            response = response[:-1]
        
        # Final cleanup
        response = response.strip()
        
        # If we somehow ended up with empty response after polishing
        if not response or len(response.strip()) < 3:
            logger.warning("Response too short after polishing, using fallback")
            return self._get_fallback_response()
        
        # If response still seems too formal/long, use fallback
        if len(response) > 250 or any(phrase in response.lower() for phrase in ['everyone', 'alright', 'should be', 'how about']):
            logger.warning(f"Response still too formal after polishing: {response[:50]}... using fallback")
            return self._get_fallback_response()
        
        return response
    
    def _get_fallback_response(self) -> str:
        """
        Get a fallback response if AI fails.
        
        Returns:
            Random casual response
        """
        return random.choice(CASUAL_RESPONSES)
