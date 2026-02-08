#!/usr/bin/env python3
"""
Game Library Setup Script

Populates Mitch's game library with your gaming group's games.
Can also list current games or clear the library.

Usage:
    python3 scripts/setup_games.py populate    # Add all games to library
    python3 scripts/setup_games.py list        # Show current game library
    python3 scripts/setup_games.py clear       # Clear library (with confirmation)
    python3 scripts/setup_games.py stats       # Show database statistics
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from game_tracker import GameTracker
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


# Your gaming group's library - customize player counts and tags as needed!
GAMES = [
    # Co-op Survival/Mining
    {
        "name": "Deep Rock Galactic",
        "min": 1,
        "max": 4,
        "category": "co-op",
        "tags": ["shooter", "mining", "dwarves"]
    },
    {
        "name": "Return To Moria",
        "min": 1,
        "max": 8,
        "category": "co-op",
        "tags": ["survival", "mining", "crafting", "lotr"]
    },
    
    # Co-op Horror
    {
        "name": "Lethal Company",
        "min": 1,
        "max": 4,
        "category": "co-op",
        "tags": ["horror", "comedy", "survival"]
    },
    {
        "name": "Escape The Backrooms",
        "min": 1,
        "max": 4,
        "category": "co-op",
        "tags": ["horror", "exploration", "backrooms"]
    },
    
    # Co-op Action/Adventure
    {
        "name": "R.E.P.O.",
        "min": 1,
        "max": 4,
        "category": "co-op",
        "tags": ["action", "sci-fi"]
    },
    {
        "name": "TMNT: Splintered Fate",
        "min": 1,
        "max": 4,
        "category": "co-op",
        "tags": ["action", "roguelike", "tmnt"]
    },
    
    # Party/Casual
    {
        "name": "RV There Yet?",
        "min": 2,
        "max": 4,
        "category": "party",
        "tags": ["casual", "driving", "chaotic"]
    },
    {
        "name": "Liar's Bar",
        "min": 2,
        "max": 4,
        "category": "party",
        "tags": ["bluffing", "cards", "social"]
    },
    {
        "name": "PEAK",
        "min": 2,
        "max": 4,
        "category": "party",
        "tags": ["climbing", "physics", "challenging"]
    },
    
    # Challenging Co-op
    {
        "name": "Chained Together",
        "min": 2,
        "max": 4,
        "category": "co-op",
        "tags": ["platformer", "challenging", "physics"]
    },
]


def populate_games(tracker: GameTracker):
    """Add all games to the library."""
    print("\nSetting up Mitch's game library...")
    print("=" * 50)
    
    added_count = 0
    skipped_count = 0
    
    for game_data in GAMES:
        game_id = tracker.add_game(
            name=game_data["name"],
            min_players=game_data["min"],
            max_players=game_data["max"],
            category=game_data.get("category"),
            tags=game_data.get("tags", [])
        )
        
        if game_id:
            # Format tags for display
            tags_str = ", ".join(game_data.get("tags", [])) if game_data.get("tags") else "no tags"
            print(f"✓ Added {game_data['name']} ({game_data['min']}-{game_data['max']} players, {game_data.get('category', 'uncategorized')})")
            added_count += 1
        else:
            print(f"⊘ Skipped {game_data['name']} (already exists)")
            skipped_count += 1
    
    print("=" * 50)
    print(f"\n✓ Library setup complete!")
    print(f"  Added: {added_count} games")
    if skipped_count > 0:
        print(f"  Skipped: {skipped_count} games (already existed)")


def list_games(tracker: GameTracker):
    """Display all games in the library."""
    games = tracker.get_all_games()
    
    if not games:
        print("\nMitch's game library is empty!")
        print("Run 'python3 scripts/setup_games.py populate' to add games.\n")
        return
    
    print(f"\nMitch's Game Library ({len(games)} games):")
    print("=" * 80)
    
    # Group by category
    categories = {}
    for game in games:
        cat = game['category'] or 'uncategorized'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(game)
    
    # Display by category
    for category, cat_games in sorted(categories.items()):
        print(f"\n{category.upper()}:")
        for game in sorted(cat_games, key=lambda g: g['name']):
            tags_str = ", ".join(game['tags']) if game['tags'] else "no tags"
            print(f"  • {game['name']} ({game['min_players']}-{game['max_players']} players) - {tags_str}")
    
    print("=" * 80)
    print()


def clear_games(tracker: GameTracker):
    """Clear all games from the library (with confirmation)."""
    print("\n⚠️  WARNING: This will delete ALL games, play history, and suggestions!")
    response = input("Are you sure? Type 'yes' to confirm: ")
    
    if response.lower() == 'yes':
        if tracker.clear_all_games():
            print("✓ Library cleared successfully.\n")
        else:
            print("✗ Failed to clear library.\n")
    else:
        print("✓ Cancelled - nothing was deleted.\n")


def show_stats(tracker: GameTracker):
    """Display database statistics."""
    stats = tracker.get_stats()
    
    print("\nMitch Database Statistics:")
    print("=" * 50)
    print(f"  Total Games: {stats['total_games']}")
    print(f"  Total Plays: {stats['total_plays']}")
    print(f"  Total Suggestions: {stats['total_suggestions']}")
    print("=" * 50)
    
    # If there are suggestions, show suggestion stats
    if stats['total_suggestions'] > 0:
        suggestion_stats = tracker.get_suggestion_stats()
        print("\nSuggestion Analytics:")
        print(f"  Acceptance Rate: {suggestion_stats['acceptance_rate']}%")
        print(f"  Recent (30 days): {suggestion_stats['recent_suggestions']}")
        
        if suggestion_stats['top_suggested_games']:
            print("\n  Top Suggested Games:")
            for game in suggestion_stats['top_suggested_games']:
                print(f"    • {game['name']}: {game['suggestion_count']} times")
    
    print()


def main():
    """Main script entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/setup_games.py populate    # Add games to library")
        print("  python3 scripts/setup_games.py list        # Show current library")
        print("  python3 scripts/setup_games.py clear       # Clear library")
        print("  python3 scripts/setup_games.py stats       # Show statistics")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Initialize tracker
    tracker = GameTracker()
    
    # Execute command
    if command == 'populate':
        populate_games(tracker)
    elif command == 'list':
        list_games(tracker)
    elif command == 'clear':
        clear_games(tracker)
    elif command == 'stats':
        show_stats(tracker)
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: populate, list, clear, stats")
        sys.exit(1)


if __name__ == '__main__':
    main()
