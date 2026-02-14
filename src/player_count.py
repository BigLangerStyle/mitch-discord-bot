"""
Suggestion Engine - Player Count Parsing and Game Suggestion Logic

Handles intelligent player count extraction from messages and provides
clarification when counts are ambiguous.
"""

import re
from typing import Optional, Tuple

# Word to number mapping (one through fifteen)
# Covers most common casual chat usage
WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15
}


def extract_player_count(message_content: str) -> Optional[int]:
    """
    Extract explicit player count from message if mentioned.
    
    Searches for patterns like:
    - "5 of us"
    - "three people"
    - "game for 8 players"
    - "2 peeps"
    
    Args:
        message_content: The Discord message text to parse
    
    Returns:
        int or None: Player count if found (1-99), None if not mentioned
    
    Examples:
        >>> extract_player_count("5 of us want to play")
        5
        >>> extract_player_count("three people here")
        3
        >>> extract_player_count("what should we play")
        None
        >>> extract_player_count("game for 8 players")
        8
    """
    content_lower = message_content.lower()
    
    # Try digits first (1-99)
    # Matches: "5 of us", "3 people", "7 players", "2 peeps"
    digit_match = re.search(r'\b(\d+)\s*(?:of us|people|players?|peeps)', content_lower)
    if digit_match:
        count = int(digit_match.group(1))
        if 1 <= count <= 99:  # Sanity check for reasonable group size
            return count
    
    # Try word numbers (one through fifteen)
    # Matches: "three people", "five of us", "two players"
    for word, num in WORD_TO_NUM.items():
        pattern = rf'\b{word}\s+(?:of us|people|players?|peeps)'
        if re.search(pattern, content_lower):
            return num
    
    return None


def should_ask_for_count(extracted_count: Optional[int], online_count: int) -> Tuple[bool, Optional[int]]:
    """
    Decide if we should ask for player count clarification.
    
    Logic:
    - If explicit count mentioned: use it, don't ask
    - If 4+ online and no explicit count: use online count, don't ask (clear group)
    - If 2-3 online and no explicit count: ask for clarification (ambiguous)
    - If 1 online and no explicit count: ask if solo or group
    
    Args:
        extracted_count: Explicit count from message (or None if not found)
        online_count: Number of online Discord members
    
    Returns:
        tuple: (should_ask: bool, use_count: int or None)
        
        If should_ask is True, use_count will be None (need to ask first)
        If should_ask is False, use_count is the count to use for suggestions
    
    Examples:
        >>> should_ask_for_count(5, 3)  # Explicit count mentioned
        (False, 5)
        >>> should_ask_for_count(None, 6)  # 6 online, clear group
        (False, 6)
        >>> should_ask_for_count(None, 2)  # 2 online, ambiguous
        (True, None)
        >>> should_ask_for_count(None, 1)  # 1 online, solo or group?
        (True, None)
    """
    # Explicit count always takes precedence
    if extracted_count is not None:
        return (False, extracted_count)
    
    # Clear group (4+ online) - no need to ask
    if online_count >= 4:
        return (False, online_count)
    
    # Ambiguous (1-3 online, no explicit count) - ask for clarification
    return (True, None)


def get_clarification_message(online_count: int) -> str:
    """
    Get appropriate clarification question based on online count.
    
    Messages are casual and brief, matching Mitch's personality.
    
    Args:
        online_count: Number of online Discord members
    
    Returns:
        str: Clarification question to ask user
    
    Examples:
        >>> get_clarification_message(1)
        'just you? or are more joining later?'
        >>> get_clarification_message(2)
        'just you two? or are more people playing?'
        >>> get_clarification_message(3)
        'just the three of you? or is it a bigger group?'
    """
    if online_count == 1:
        return "just you? or are more joining later?"
    elif online_count == 2:
        return "just you two? or are more people playing?"
    elif online_count == 3:
        return "just the three of you? or is it a bigger group?"
    else:
        # Fallback for edge cases (shouldn't normally reach here)
        return f"just the {online_count} of you? or is it a bigger group?"
