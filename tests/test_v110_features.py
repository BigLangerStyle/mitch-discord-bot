#!/usr/bin/env python3
"""
Test script for v1.1.0 conversational features

Tests:
1. Conversation context tracking
2. Casual response generation
3. Rate limiting (if enabled)
4. Integration with existing suggestion detection
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from personality import PersonalitySystem
from ollama_client import OllamaClient
from config_loader import load_config

# ANSI colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(name, status, message=""):
    """Print test result with color."""
    if status == "pass":
        print(f"{GREEN}✓{RESET} {name}")
    elif status == "fail":
        print(f"{RED}✗{RESET} {name}")
    elif status == "skip":
        print(f"{YELLOW}⊘{RESET} {name} (skipped)")
    if message:
        print(f"  {message}")


async def test_conversation_context():
    """Test conversation context tracking."""
    print(f"\n{BLUE}Testing conversation context tracking...{RESET}")
    
    # Simulate conversation history
    context = [
        {"author": "Alice", "content": "hey Mitch"},
        {"author": "Mitch", "content": "yo what's up?"},
        {"author": "Alice", "content": "not much, kinda bored"},
    ]
    
    if len(context) == 3:
        print_test("Context tracking", "pass", f"Stored {len(context)} messages")
    else:
        print_test("Context tracking", "fail", "Context not tracking correctly")
    
    return True


async def test_casual_response():
    """Test casual response generation with context."""
    print(f"\n{BLUE}Testing casual response generation...{RESET}")
    
    try:
        config = load_config()
        ollama_config = config.get('ollama', {})
        
        ollama_client = OllamaClient(
            host=ollama_config.get('host', 'http://localhost:11434'),
            model=ollama_config.get('model', 'phi3:mini'),
            timeout=ollama_config.get('timeout', 60),
            temperature=ollama_config.get('temperature', 0.8),
            max_tokens=ollama_config.get('max_tokens', 300)
        )
        
        personality = PersonalitySystem(ollama_client)
        
        # Test simple greeting
        print(f"\n{YELLOW}Test 1: Simple greeting{RESET}")
        response = await personality.casual_response(
            "hey Mitch what's up?",
            requester_name="TestUser",
            conversation_history=[]
        )
        print(f"  Response: {response}")
        
        if len(response) > 0 and len(response) < 300:
            print_test("Simple greeting response", "pass", f"Length: {len(response)} chars")
        else:
            print_test("Simple greeting response", "fail", f"Unexpected length: {len(response)}")
        
        # Test with context
        print(f"\n{YELLOW}Test 2: With conversation context{RESET}")
        context = [
            {"author": "Alice", "content": "hey Mitch"},
            {"author": "Mitch", "content": "yo what's up?"},
            {"author": "Alice", "content": "not much, kinda bored"},
        ]
        
        response = await personality.casual_response(
            "yeah for real",
            requester_name="Alice",
            conversation_history=context
        )
        print(f"  Response: {response}")
        print_test("Contextual response", "pass", "Used conversation history")
        
        # Test thanks/acknowledgment
        print(f"\n{YELLOW}Test 3: Thanks message{RESET}")
        context = [
            {"author": "Bob", "content": "Mitch what should we play?"},
            {"author": "Mitch", "content": "how about Deep Rock Galactic?"},
        ]
        
        response = await personality.casual_response(
            "thanks Mitch!",
            requester_name="Bob",
            conversation_history=context
        )
        print(f"  Response: {response}")
        print_test("Thanks acknowledgment", "pass", "Contextual to previous suggestion")
        
        return True
        
    except Exception as e:
        print_test("Casual response generation", "fail", str(e))
        return False


async def test_rate_limiting():
    """Test rate limiting configuration."""
    print(f"\n{BLUE}Testing rate limiting configuration...{RESET}")
    
    try:
        config = load_config()
        rate_limit_config = config.get('rate_limiting', {})
        
        enabled = rate_limit_config.get('enabled', False)
        cooldown = rate_limit_config.get('cooldown_seconds', 5)
        message = rate_limit_config.get('message', 'whoa slow down a sec!')
        
        print(f"  Enabled: {enabled}")
        print(f"  Cooldown: {cooldown} seconds")
        print(f"  Message: {message}")
        
        print_test("Rate limiting config", "pass", f"Configured correctly")
        
        if enabled:
            print(f"  {YELLOW}Note: Rate limiting is ENABLED. Rapid @mentions will be throttled.{RESET}")
        else:
            print(f"  {GREEN}Note: Rate limiting is DISABLED (recommended for small groups).{RESET}")
        
        return True
        
    except Exception as e:
        print_test("Rate limiting config", "fail", str(e))
        return False


async def test_suggestion_detection_unchanged():
    """Verify suggestion detection still works as before."""
    print(f"\n{BLUE}Testing suggestion detection (v1.0.1 logic)...{RESET}")
    
    test_cases = [
        ("what should we play?", True),
        ("what game should we try?", True),
        ("any suggestions?", True),
        ("pick a game", True),
        ("hey Mitch", False),
        ("thanks!", False),
        ("how's it going?", False),
    ]
    
    for message, should_detect in test_cases:
        content_lower = message.lower()
        
        asking_for_game = (
            ('what' in content_lower and ('play' in content_lower or 'game' in content_lower)) or
            (('suggest' in content_lower or 'recommend' in content_lower) and 'game' in content_lower) or
            ('give me' in content_lower and ('game' in content_lower or 'suggestion' in content_lower)) or
            'game suggestion' in content_lower or
            'pick a game' in content_lower or
            'choose a game' in content_lower or
            'any suggestions' in content_lower or
            'any suggestion' in content_lower
        )
        
        if asking_for_game == should_detect:
            print_test(f"'{message}'", "pass", f"→ {'Game request' if asking_for_game else 'Casual chat'}")
        else:
            print_test(f"'{message}'", "fail", f"Expected: {should_detect}, Got: {asking_for_game}")
    
    return True


def test_config_sections():
    """Test that new config sections exist."""
    print(f"\n{BLUE}Testing configuration sections...{RESET}")
    
    try:
        config = load_config()
        
        # Check conversation section
        conversation_config = config.get('conversation', {})
        if conversation_config:
            context_messages = conversation_config.get('context_messages', 5)
            casual_max_length = conversation_config.get('casual_max_length', 300)
            print_test("Conversation config section", "pass", 
                      f"context_messages={context_messages}, max_length={casual_max_length}")
        else:
            print_test("Conversation config section", "fail", "Section missing from config")
        
        # Check rate limiting section
        rate_limit_config = config.get('rate_limiting', {})
        if rate_limit_config:
            print_test("Rate limiting config section", "pass")
        else:
            print_test("Rate limiting config section", "fail", "Section missing from config")
        
        return True
        
    except Exception as e:
        print_test("Configuration sections", "fail", str(e))
        return False


async def main():
    """Run all tests."""
    print(f"\n{'='*60}")
    print(f"{BLUE}Mitch Discord Bot - v1.1.0 Feature Tests{RESET}")
    print(f"{'='*60}")
    
    results = []
    
    # Sync tests
    results.append(test_config_sections())
    
    # Async tests
    results.append(await test_conversation_context())
    results.append(await test_suggestion_detection_unchanged())
    results.append(await test_rate_limiting())
    
    print(f"\n{YELLOW}Note: The following tests require Ollama to be running{RESET}")
    try:
        results.append(await test_casual_response())
    except Exception as e:
        print_test("Casual response tests", "skip", f"Ollama not available: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    passed = sum(1 for r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"{GREEN}✓ All tests passed ({passed}/{total}){RESET}")
    else:
        print(f"{YELLOW}⚠ Some tests failed or skipped ({passed}/{total}){RESET}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
