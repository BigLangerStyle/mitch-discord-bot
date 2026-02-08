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

# Fallback responses if AI is unavailable or too formal
CASUAL_RESPONSES = [
    "yo what's up?",
    "hey, not sure what to suggest yet",
    "hmm tough call",
    "sup, what kind of game you thinking?",
    "idk what's the vibe?"
]

# Simple game suggestion fallbacks (used by suggestion engine)
SUGGESTION_FALLBACKS = [
    "hmm maybe {game}?",
    "how about {game}",
    "try {game}?",
    "{game} could work",
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

# Patterns that indicate the AI is being too chatty/descriptive
FORMALITY_INDICATORS = [
    r"hey \w+,",  # "hey Brad," or "hey [name],"
    r"since you",
    r"since [a-z]",
    r"haven't played",
    r"no recent",
    r"just picked up",
    r"I just found",
    r"it epic",
    r"pretty cool",
    r"offers? a (?:fresh|new|unique|different)",
    r"take on",
    r"without .+ing",
    r"twisted .+line",
    r"with (?:its|their|the)",
    r"always fun to",
    r"a bit scared",
    r"want to game",
    r"checking in",
    r"Plus[,.]",
    r"so why not",
    r"let's go with",
    r"\. [A-Z]",  # Sentence starting mid-response (too chatty)
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
        # Build the full prompt
        full_prompt = self._build_prompt(user_message, context)
        
        try:
            logger.info("Generating AI response...")
            raw_response = await self.ollama.generate(full_prompt)
            
            # Polish the response to keep it casual
            polished = self._polish_response(raw_response)
            
            # Check if response is still too formal/chatty after polishing
            if self._is_too_formal(polished):
                logger.warning(f"Response too formal/chatty: {polished[:60]}... using fallback")
                return self._get_fallback_response()
            
            logger.info(f"Response generated: {len(polished)} chars")
            return polished
            
        except Exception as e:
            logger.warning(f"AI generation failed: {e}, using fallback")
            return self._get_fallback_response()
    
    def _build_prompt(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build the full prompt to send to AI.
        
        If context is provided with game suggestion info, treats user_message as 
        the complete pre-built prompt from suggestion_engine.
        Otherwise builds general conversation prompt.
        
        Args:
            user_message: The user's message (or complete prompt for suggestions)
            context: Optional context information (player count, filtered_games, etc.)
            
        Returns:
            Complete prompt string
        """
        # Check if this is a suggestion request with context
        if context and 'filtered_games' in context:
            # This is a suggestion request - user_message is already the full prompt
            # from suggestion_engine, so just return it as-is
            return user_message
        
        # Otherwise, build normal conversational prompt
        # Start with system prompt
        prompt_parts = [SYSTEM_PROMPT]
        
        # Add context if provided (for general conversation)
        if context:
            prompt_parts.append("\nCONTEXT:")
            if "player_count" in context:
                prompt_parts.append(f"Players online: {context['player_count']}")
            if "recent_games" in context:
                games = ", ".join(context["recent_games"])
                prompt_parts.append(f"Recently played: {games}")
        
        # Add the actual user message
        prompt_parts.append(f"\nUSER: {user_message}")
        prompt_parts.append("\nMITCH (brief casual response, no quotes, no emojis):")
        
        return "\n".join(prompt_parts)
    
    def _polish_response(self, raw_response: str) -> str:
        """
        Polish AI response to keep it casual and brief.
        
        Aggressively removes corporate language, excessive punctuation,
        emojis, quotes, and ensures the response fits Mitch's personality.
        
        Args:
            raw_response: Raw text from AI
            
        Returns:
            Polished response text
        """
        response = raw_response.strip()
        
        # Remove surrounding quotes (single or double)
        response = re.sub(r'^["\']|["\']$', '', response)
        response = re.sub(r'^["\'](.+)["\']$', r'\1', response)
        
        # Remove everything after certain markers (AI instruction artifacts)
        response = re.split(r'---+', response)[0]
        response = re.split(r'\*\*Instruction', response)[0]
        response = re.split(r'USER:', response, flags=re.IGNORECASE)[0]
        response = re.split(r'MITCH:', response, flags=re.IGNORECASE)[0]
        
        # Remove all emojis completely
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\u2600-\u26FF\u2700-\u27BF]'
        response = re.sub(emoji_pattern, '', response)
        
        # Remove "hey [name]," greetings at start
        response = re.sub(r'^hey \w+,\s*', '', response, flags=re.IGNORECASE)
        
        # Remove corporate and enthusiasm phrases
        for phrase in CORPORATE_PHRASES + ENTHUSIASM_PHRASES:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        # Remove common filler words at the start
        response = re.sub(r'^(?:Well,?|So,?|Hmm,?)\s+', '', response, flags=re.IGNORECASE)
        
        # Reduce excessive exclamation marks
        response = re.sub(r'!+', '!', response)
        
        # Clean up excessive punctuation
        response = re.sub(r'\?{2,}', '?', response)
        response = re.sub(r'\.{4,}', '...', response)
        response = re.sub(r'[!?]{2,}', '?', response)
        response = re.sub(r'([.!?])\1+$', r'\1', response)
        
        # Clean up whitespace
        response = re.sub(r'\n\s*\n', '\n', response)
        response = re.sub(r'  +', ' ', response)
        response = response.strip()
        
        # If response has multiple sentences, keep only first
        # This is aggressive but necessary to keep it brief
        sentences = re.split(r'(?<=[.!?])\s+', response)
        if len(sentences) > 1:
            # Just keep the first sentence
            response = sentences[0]
        
        # Enforce very strict length limit
        if len(response) > 80:
            # Try to cut at sentence boundary
            if '?' in response:
                response = response.split('?')[0] + '?'
            elif '.' in response:
                response = response.split('.')[0]
            else:
                # Just truncate
                response = response[:77] + '...'
        
        # Lowercase the first letter unless it's "I" or a proper noun
        if response and len(response) > 0:
            if response[0].isupper() and response[0] != 'I' and not response[0:2].isupper():
                response = response[0].lower() + response[1:]
        
        # Remove trailing periods (casual text style)
        if response.endswith('.') and not response.endswith('...'):
            response = response[:-1]
        
        # Final cleanup
        response = response.strip()
        response = response.strip('"\'')
        
        # If we ended up with empty response after polishing
        if not response or len(response.strip()) < 3:
            logger.warning("Response too short after polishing")
            return self._get_fallback_response()
        
        return response
    
    def _is_too_formal(self, response: str) -> bool:
        """
        Check if response is still too formal/chatty after polishing.
        
        This is VERY strict - even slightly chatty responses get rejected.
        
        Args:
            response: Polished response text
            
        Returns:
            True if response should be replaced with fallback
        """
        response_lower = response.lower()
        
        # Reject if over 80 chars (too chatty)
        if len(response) > 80:
            logger.debug(f"Too long: {len(response)} chars")
            return True
        
        # Reject if has period mid-sentence (multiple thoughts)
        if '. ' in response:
            logger.debug("Multiple sentences detected")
            return True
        
        # Check for formality/chattiness indicators
        for pattern in FORMALITY_INDICATORS:
            if re.search(pattern, response_lower):
                logger.debug(f"Formality pattern: {pattern}")
                return True
        
        # Reject common chatty words
        chatty_words = ['just', 'pretty', 'really', 'actually', 'totally', 'definitely']
        if any(word in response_lower for word in chatty_words):
            logger.debug(f"Chatty word detected")
            return True
        
        return False
    
    def _get_fallback_response(self) -> str:
        """
        Get a fallback response if AI fails or is too formal.
        
        Returns:
            Random casual response
        """
        return random.choice(CASUAL_RESPONSES)
