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
5. NO corporate language
6. NO making up game names - if you don't know, say so
7. Be honest when you don't have information
8. Sound like a friend texting, not a customer service bot
9. DO NOT wrap your response in quotes

GOOD RESPONSES (copy this exact casual style):
yo
sup?
hmm not sure - co-op or competitive?
idk, what's the vibe?
lol you guys just played that yesterday
maybe something for 4 people?
not sure what you got

BAD RESPONSES (never do this):
"Hey! How 'bout a quick match?"
Hey everyone! What's got you feeling lucky today?
I'd be happy to help! What do you think?
Let me recommend something for your crew size
"ready for some gaming fun?"

Remember: You're texting a friend. Super casual. No quotes. No exclamation marks unless actually excited."""

# Fallback responses if AI is unavailable
CASUAL_RESPONSES = [
    "yo what's up?",
    "hey, not sure what to suggest yet",
    "hmm tough call",
    "sup, what kind of game you thinking?",
    "idk what's the vibe?"
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
    r"How 'bout",
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
    r"ready for some gaming fun",
]

# Extra strict phrases for GAME SUGGESTIONS only
SUGGESTION_FORMALITY = [
    r"check out",
    r"checking out",
    r"give .+ a try",
    r"why not\??",
    r"since you",
    r"since [a-z]",
    r"offers? a",
    r"without .+ing",
    r"for a twisted",
    r"that .+ touch",
    r"with its .+ concept",
    r"I just found",
    r"it epic",
    r"pretty cool",
    r"Plus,",
    r"so why not",
    r"let's go with",
    r"Just picked up",
    r"jump into",
    r"see who can",
    r"see if you",
    r"hey \w+,",  # "hey Brad," etc
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
            user_message: The message from the user (or pre-built prompt for suggestions)
            context: Optional context dict (player_count, filtered_games, recent_games, etc.)
                    If context contains 'filtered_games', treats user_message as complete prompt
                    
        Returns:
            Polished response text ready to send
        """
        # Check if this is a game suggestion request
        is_suggestion = context and 'filtered_games' in context
        
        # Build the full prompt
        full_prompt = self._build_prompt(user_message, context)
        
        try:
            logger.info("Generating AI response...")
            raw_response = await self.ollama.generate(full_prompt)
            
            # Polish the response
            polished = self._polish_response(raw_response, strict=is_suggestion)
            
            # Only apply strict formality check to suggestions
            if is_suggestion and self._is_too_formal_for_suggestion(polished):
                logger.warning(f"Suggestion too formal: {polished[:60]}... using simple format")
                # Extract game name and use simple format
                return self._simple_suggestion_fallback(context)
            
            logger.info(f"Response generated: {len(polished)} chars")
            return polished
            
        except Exception as e:
            logger.warning(f"AI generation failed: {e}, using fallback")
            if is_suggestion:
                return self._simple_suggestion_fallback(context)
            return self._get_fallback_response()
    
    def _build_prompt(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build the full prompt to send to AI.
        
        Args:
            user_message: The user's message (or complete prompt for suggestions)
            context: Optional context information
            
        Returns:
            Complete prompt string
        """
        # Check if this is a suggestion request with context
        if context and 'filtered_games' in context:
            # Pre-built prompt from suggestion_engine
            return user_message
        
        # Normal conversational prompt
        prompt_parts = [SYSTEM_PROMPT]
        
        if context:
            prompt_parts.append("\nCONTEXT:")
            if "player_count" in context:
                prompt_parts.append(f"Players online: {context['player_count']}")
            if "recent_games" in context:
                games = ", ".join(context["recent_games"])
                prompt_parts.append(f"Recently played: {games}")
        
        prompt_parts.append(f"\nUSER: {user_message}")
        prompt_parts.append("\nMITCH (brief casual response, no quotes, no emojis):")
        
        return "\n".join(prompt_parts)
    
    def _polish_response(self, raw_response: str, strict: bool = False) -> str:
        """
        Polish AI response to keep it casual and brief.
        
        Args:
            raw_response: Raw text from AI
            strict: If True, apply extra strict filters (for game suggestions)
            
        Returns:
            Polished response text
        """
        response = raw_response.strip()
        
        # Remove surrounding quotes
        response = re.sub(r'^["\']|["\']$', '', response)
        response = re.sub(r'^["\'](.+)["\']$', r'\1', response)
        
        # Remove instruction artifacts
        response = re.split(r'---+', response)[0]
        response = re.split(r'\*\*Instruction', response)[0]
        response = re.split(r'USER:', response, flags=re.IGNORECASE)[0]
        response = re.split(r'MITCH:', response, flags=re.IGNORECASE)[0]
        
        # Remove emojis
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\u2600-\u26FF\u2700-\u27BF]'
        response = re.sub(emoji_pattern, '', response)
        
        # Remove corporate phrases (always)
        for phrase in CORPORATE_PHRASES + ENTHUSIASM_PHRASES:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        # Remove suggestion-specific formal phrases (only if strict mode)
        if strict:
            for phrase in SUGGESTION_FORMALITY:
                response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        # Remove filler words at start
        response = re.sub(r'^(?:Well,?|So,?|Hmm,?)\s+', '', response, flags=re.IGNORECASE)
        
        # Clean up punctuation
        response = re.sub(r'!+', '!', response)
        response = re.sub(r'\?{2,}', '?', response)
        response = re.sub(r'\.{4,}', '...', response)
        response = re.sub(r'[!?]{2,}', '?', response)
        response = re.sub(r'([.!?])\1+$', r'\1', response)
        
        # Clean up whitespace
        response = re.sub(r'\n\s*\n', '\n', response)
        response = re.sub(r'  +', ' ', response)
        response = response.strip()
        
        # For suggestions, keep it VERY brief
        if strict and len(response) > 100:
            # Take first sentence only
            sentences = re.split(r'[.!?]\s+', response)
            response = sentences[0]
            if not response.endswith(('?', '!', '...')):
                response = response.rstrip('.')
        
        # Lowercase first letter unless proper noun
        if response and len(response) > 0:
            if response[0].isupper() and response[0] != 'I' and not response[0:2].isupper():
                response = response[0].lower() + response[1:]
        
        # Remove trailing periods (casual style)
        if response.endswith('.') and not response.endswith('...'):
            response = response[:-1]
        
        response = response.strip().strip('"\'')
        
        if not response or len(response) < 3:
            return self._get_fallback_response()
        
        return response
    
    def _is_too_formal_for_suggestion(self, response: str) -> bool:
        """
        Check if a GAME SUGGESTION is too formal/chatty.
        
        This is ONLY for suggestions, not general conversation.
        
        Args:
            response: Polished response text
            
        Returns:
            True if too formal for a game suggestion
        """
        response_lower = response.lower()
        
        # Too long for a suggestion
        if len(response) > 100:
            return True
        
        # Multiple sentences in suggestion
        if '. ' in response:
            return True
        
        # Chatty words that don't fit suggestions
        chatty_words = ['just', 'pretty', 'really', 'actually', 'totally']
        if any(word in response_lower for word in chatty_words):
            return True
        
        # Question with elaboration
        if '?' in response and ' and ' in response_lower:
            return True
        
        return False
    
    def _simple_suggestion_fallback(self, context: Dict[str, Any]) -> str:
        """
        Generate a simple game suggestion when AI is too chatty.
        
        Args:
            context: Context dict with filtered_games
            
        Returns:
            Simple suggestion string
        """
        filtered_games = context.get('filtered_games', [])
        
        if not filtered_games:
            return "hmm not sure what to suggest"
        
        # Pick 1-2 games randomly
        num_games = min(2, len(filtered_games))
        selected = random.sample(filtered_games, num_games)
        
        if num_games == 1:
            templates = [
                f"how about {selected[0]['name']}?",
                f"maybe {selected[0]['name']}",
                f"try {selected[0]['name']}",
                f"{selected[0]['name']}?"
            ]
        else:
            templates = [
                f"how about {selected[0]['name']} or {selected[1]['name']}?",
                f"maybe {selected[0]['name']} or {selected[1]['name']}",
                f"{selected[0]['name']} or {selected[1]['name']}?",
            ]
        
        return random.choice(templates)
    
    def _get_fallback_response(self) -> str:
        """
        Get a fallback response if AI completely fails.
        
        Returns:
            Random casual response
        """
        return random.choice(CASUAL_RESPONSES)
