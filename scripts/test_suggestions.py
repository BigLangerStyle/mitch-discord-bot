#!/usr/bin/env python3
"""
Interactive Suggestion Testing Utility

Tests Mitch's suggestion engine without needing Discord.
Allows interactive testing of different player counts and scenarios.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_loader import load_config
from logger import setup_logging
from ollama_client import OllamaClient
from personality import PersonalitySystem
from game_tracker import GameTracker
from suggestion_engine import SuggestionEngine


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  Mitch Suggestion Testing Utility")
    print("=" * 60)
    print()


def print_filtered_games(games):
    """Print list of filtered games nicely."""
    if not games:
        print("  No games match filters!")
        return
    
    print(f"  Filtered games ({len(games)}):")
    for game in games:
        category = game.get('category', 'misc')
        players = f"{game['min_players']}-{game['max_players']}p"
        print(f"    - {game['name']} ({category}, {players})")
    print()


async def interactive_test(engine, tracker):
    """
    Run interactive testing loop.
    
    Args:
        engine: SuggestionEngine instance
        tracker: GameTracker instance
    """
    print("Commands:")
    print("  - Enter player count (1-10) to generate suggestion")
    print("  - 'stats' to see suggestion statistics")
    print("  - 'games' to list all games")
    print("  - 'plays' to see recent play history")
    print("  - 'quit' or 'exit' to exit")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("How many players? (or command): ").strip().lower()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input in ['quit', 'exit', 'q']:
                print("\nThanks for testing! 🎮")
                break
            
            elif user_input == 'stats':
                stats = tracker.get_suggestion_stats()
                print("\n📊 Suggestion Statistics:")
                print(f"  Total suggestions: {stats['total']}")
                print(f"  Accepted: {stats['accepted']}")
                if stats['total'] > 0:
                    acceptance_rate = (stats['accepted'] / stats['total']) * 100
                    print(f"  Acceptance rate: {acceptance_rate:.1f}%")
                print(f"  Recent (30 days): {stats['recent']}")
                print()
                continue
            
            elif user_input == 'games':
                games = tracker.get_all_games()
                print(f"\n📚 Game Library ({len(games)} games):")
                for game in games:
                    category = game.get('category', 'misc')
                    players = f"{game['min_players']}-{game['max_players']}p"
                    print(f"  - {game['name']} ({category}, {players})")
                print()
                continue
            
            elif user_input == 'plays':
                plays = tracker.get_recent_plays(days=7)
                print(f"\n🕹️  Recent Plays (last 7 days):")
                if not plays:
                    print("  No recent plays recorded")
                else:
                    for play in plays:
                        print(f"  - {play['game_name']} on {play['played_date'][:10]}")
                print()
                continue
            
            # Try to parse as player count
            try:
                player_count = int(user_input)
                
                if player_count < 1 or player_count > 10:
                    print("⚠️  Player count should be between 1 and 10")
                    print()
                    continue
                
                print(f"\nGenerating suggestion for {player_count} players...")
                print()
                
                # Show what games are available before filtering
                matching_games = tracker.get_games_for_players(player_count)
                print(f"Games that support {player_count} players: {len(matching_games)}")
                
                # Get filtered games (with cooldown)
                filtered_games = engine._filter_games(
                    player_count,
                    engine.cooldown_hours
                )
                
                print_filtered_games(filtered_games)
                
                # Generate suggestion
                print("⏳ Calling AI...")
                start_time = asyncio.get_event_loop().time()
                
                response = await engine.suggest_games(
                    player_count=player_count,
                    requester_name="TestUser"
                )
                
                elapsed = asyncio.get_event_loop().time() - start_time
                
                print("✨ Mitch suggests:")
                print(f"  \"{response}\"")
                print()
                print(f"⏱️  Response time: {elapsed:.1f}s")
                print()
                
                # Ask if they want to mark as played
                mark_played = input("Record a game as played? (game name or 'n'): ").strip()
                if mark_played and mark_played.lower() not in ['n', 'no', 'nope']:
                    game = tracker.get_game_by_name(mark_played)
                    if game:
                        tracker.record_play(
                            game_id=game['id'],
                            player_count=player_count
                        )
                        print(f"✓ Recorded play: {game['name']}")
                    else:
                        print(f"⚠️  Game not found: {mark_played}")
                print()
                
            except ValueError:
                print(f"⚠️  Unknown command or invalid number: {user_input}")
                print()
                continue
                
        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()


async def main():
    """Main entry point."""
    print_banner()
    
    # Load config
    print("Loading configuration...")
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        print("Make sure config/config.yaml exists and is valid")
        sys.exit(1)
    
    # Setup logging (quieter for interactive use)
    setup_logging(
        log_file=config['logging']['file'],
        log_level='WARNING',  # Less noisy for interactive testing
        max_bytes=config['logging']['max_bytes'],
        backup_count=config['logging']['backup_count']
    )
    
    # Initialize components
    print("Initializing components...")
    
    # Ollama client
    ollama_config = config.get('ollama', {})
    ollama_client = OllamaClient(
        host=ollama_config.get('host', 'http://localhost:11434'),
        model=ollama_config.get('model', 'phi3:mini'),
        timeout=ollama_config.get('timeout', 60),
        temperature=ollama_config.get('temperature', 0.8),
        max_tokens=ollama_config.get('max_tokens', 300)
    )
    
    # Check if Ollama is running
    print("Checking Ollama connection...")
    try:
        test_response = await ollama_client.generate("test")
        print("✓ Ollama connected")
    except Exception as e:
        print(f"⚠️  Ollama connection failed: {e}")
        print("Make sure Ollama is running: ollama serve")
        print("Continuing anyway (will use fallback responses)...")
    
    # Personality system
    personality = PersonalitySystem(ollama_client)
    
    # Game tracker
    tracker = GameTracker(
        db_path=config.get('database', {}).get('path', 'data/mitch.db'),
        config=config
    )
    
    # Check game library
    game_count = len(tracker.get_all_games())
    if game_count == 0:
        print("⚠️  Game library is empty!")
        print("Run: python scripts/setup_games.py populate")
        print()
        sys.exit(1)
    
    print(f"✓ Loaded {game_count} games")
    
    # Suggestion engine
    engine = SuggestionEngine(
        game_tracker=tracker,
        personality=personality,
        config=config
    )
    
    print(f"✓ Cooldown: {engine.cooldown_hours}h")
    print()
    
    # Run interactive loop
    await interactive_test(engine, tracker)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
