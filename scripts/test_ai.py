#!/usr/bin/env python3
"""
Interactive AI testing utility for Mitch Discord Bot.

Tests Ollama integration and personality system interactively
without needing to run the full Discord bot.
"""

import sys
import os
import asyncio
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_loader import load_config
from ollama_client import OllamaClient
from personality import PersonalitySystem


async def main():
    """Main interactive testing loop."""
    print("=" * 60)
    print("Mitch AI Testing Utility")
    print("=" * 60)
    
    # Load configuration
    try:
        config = load_config()
        ollama_config = config.get('ollama', {})
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Using default Ollama settings...")
        ollama_config = {
            'host': 'http://localhost:11434',
            'model': 'phi3:mini',
            'timeout': 60,
            'temperature': 0.8,
            'max_tokens': 300
        }
    
    # Initialize Ollama client
    ollama = OllamaClient(
        host=ollama_config.get('host', 'http://localhost:11434'),
        model=ollama_config.get('model', 'phi3:mini'),
        timeout=ollama_config.get('timeout', 60),
        temperature=ollama_config.get('temperature', 0.8),
        max_tokens=ollama_config.get('max_tokens', 300)
    )
    
    # Check Ollama health
    print(f"\nConnecting to Ollama at {ollama.host}...")
    if await ollama.health_check():
        print(f"✓ Connected to Ollama (model: {ollama.model})")
    else:
        print(f"✗ Cannot connect to Ollama at {ollama.host}")
        print("Make sure Ollama is running:")
        print("  - Linux: sudo systemctl start ollama")
        print("  - Windows/Mac: Start Ollama application")
        sys.exit(1)
    
    # Initialize personality system
    personality = PersonalitySystem(ollama)
    
    print("\nType your messages (Ctrl+C to quit)")
    print("-" * 60)
    
    # Interactive loop
    try:
        while True:
            # Get user input
            try:
                user_input = input("\nYou: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            # Exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # Generate response
            start_time = time.time()
            try:
                response = await personality.generate_response(user_input)
                elapsed = time.time() - start_time
                
                print(f"[Response time: {elapsed:.1f}s]")
                print(f"Mitch: {response}")
                
            except Exception as e:
                print(f"Error generating response: {e}")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    print("\nGoodbye!")


if __name__ == "__main__":
    asyncio.run(main())
