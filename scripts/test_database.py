#!/usr/bin/env python3
"""
Database Testing Utility

Tests all database operations for Mitch's game library.
Runs independent tests to verify database functionality.

Usage:
    python3 scripts/test_database.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from game_tracker import GameTracker
import logging

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings/errors during tests
    format='%(levelname)s: %(message)s'
)


class DatabaseTester:
    """Test suite for database operations."""
    
    def __init__(self):
        self.tracker = None
        self.test_db_path = 'data/test_mitch.db'
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Setup test database."""
        # Remove old test database if it exists
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.tracker = GameTracker(db_path=self.test_db_path)
        
    def cleanup(self):
        """Cleanup test database."""
        if self.tracker:
            self.tracker.close()
        
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        # Also clean up WAL files if they exist
        wal_files = [
            self.test_db_path + '-wal',
            self.test_db_path + '-shm'
        ]
        for wal_file in wal_files:
            if os.path.exists(wal_file):
                os.remove(wal_file)
        
    def assert_test(self, condition, test_name):
        """Assert a test condition."""
        if condition:
            print(f"✓ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"✗ {test_name}")
            self.failed += 1
            return False
            
    def test_database_init(self):
        """Test database initialization."""
        print("\n[1] Testing Database Initialization")
        print("-" * 50)
        
        # Database file should exist
        self.assert_test(
            os.path.exists(self.test_db_path),
            "Database file created"
        )
        
        # Should be able to get stats (verifies tables exist)
        try:
            stats = self.tracker.get_stats()
            self.assert_test(True, "Database tables created")
            self.assert_test(
                stats['total_games'] == 0,
                "Initial game count is 0"
            )
        except Exception as e:
            self.assert_test(False, f"Database tables created - {e}")
            
    def test_add_games(self):
        """Test adding games to library."""
        print("\n[2] Testing Add Games")
        print("-" * 50)
        
        # Add a game
        game_id = self.tracker.add_game(
            name="Test Game",
            min_players=2,
            max_players=4,
            category="test",
            tags=["testing", "sample"]
        )
        
        self.assert_test(
            game_id is not None,
            "Added game successfully"
        )
        
        # Try to add duplicate (should fail)
        duplicate_id = self.tracker.add_game(
            name="Test Game",
            min_players=1,
            max_players=1
        )
        
        self.assert_test(
            duplicate_id is None,
            "Duplicate game rejected"
        )
        
        # Add another game
        game_id2 = self.tracker.add_game(
            name="Another Game",
            min_players=1,
            max_players=10
        )
        
        self.assert_test(
            game_id2 is not None,
            "Added second game"
        )
        
    def test_query_games(self):
        """Test querying games."""
        print("\n[3] Testing Game Queries")
        print("-" * 50)
        
        # Get all games
        all_games = self.tracker.get_all_games()
        self.assert_test(
            len(all_games) == 2,
            f"Found 2 games in library (got {len(all_games)})"
        )
        
        # Get game by name (case-insensitive)
        game = self.tracker.get_game_by_name("test game")
        self.assert_test(
            game is not None and game['name'] == "Test Game",
            "Found game by name (case-insensitive)"
        )
        
        # Get games for specific player count
        games_for_3 = self.tracker.get_games_for_players(3)
        self.assert_test(
            len(games_for_3) == 2,
            f"Found games for 3 players (expected 2, got {len(games_for_3)})"
        )
        
        games_for_5 = self.tracker.get_games_for_players(5)
        self.assert_test(
            len(games_for_5) == 1,
            f"Found games for 5 players (expected 1, got {len(games_for_5)})"
        )
        
    def test_play_history(self):
        """Test recording play history."""
        print("\n[4] Testing Play History")
        print("-" * 50)
        
        # Get a game to record play for
        game = self.tracker.get_game_by_name("Test Game")
        
        if not game:
            self.assert_test(False, "Could not find game for play history test")
            return
        
        # Record a play
        play_id = self.tracker.record_play(
            game_id=game['id'],
            player_count=4,
            notes="Test play session"
        )
        
        self.assert_test(
            play_id is not None,
            "Recorded play session"
        )
        
        # Get recent plays
        recent_plays = self.tracker.get_recent_plays(days=7)
        self.assert_test(
            len(recent_plays) == 1,
            f"Found recent play (expected 1, got {len(recent_plays)})"
        )
        
        if recent_plays:
            play = recent_plays[0]
            self.assert_test(
                play['game_name'] == "Test Game",
                "Play history includes game name"
            )
            self.assert_test(
                play['player_count'] == 4,
                "Play history includes player count"
            )
        
    def test_suggestions(self):
        """Test suggestion tracking."""
        print("\n[5] Testing Suggestion Tracking")
        print("-" * 50)
        
        # Get a game
        game = self.tracker.get_game_by_name("Test Game")
        
        if not game:
            self.assert_test(False, "Could not find game for suggestion test")
            return
        
        # Record a suggestion
        suggestion_id = self.tracker.record_suggestion(
            game_id=game['id'],
            context="4 players online"
        )
        
        self.assert_test(
            suggestion_id is not None,
            "Recorded suggestion"
        )
        
        # Get suggestion stats
        stats = self.tracker.get_suggestion_stats()
        self.assert_test(
            stats['total_suggestions'] == 1,
            "Suggestion count updated"
        )
        
        # Mark suggestion as accepted
        accepted = self.tracker.mark_suggestion_accepted(suggestion_id)
        self.assert_test(
            accepted,
            "Marked suggestion as accepted"
        )
        
        # Verify acceptance rate
        stats = self.tracker.get_suggestion_stats()
        self.assert_test(
            stats['acceptance_rate'] == 100.0,
            f"Acceptance rate correct (expected 100%, got {stats['acceptance_rate']}%)"
        )
        
    def test_foreign_keys(self):
        """Test foreign key constraints."""
        print("\n[6] Testing Foreign Key Constraints")
        print("-" * 50)
        
        # Get initial counts
        initial_stats = self.tracker.get_stats()
        initial_plays = len(self.tracker.get_recent_plays(days=365))
        
        # Get a game with play history
        game = self.tracker.get_game_by_name("Test Game")
        
        if not game:
            self.assert_test(False, "Could not find game for FK test")
            return
        
        # Delete the game
        deleted = self.tracker.delete_game(game['id'])
        self.assert_test(
            deleted,
            "Deleted game"
        )
        
        # Play history should be gone (CASCADE)
        current_plays = len(self.tracker.get_recent_plays(days=365))
        self.assert_test(
            current_plays < initial_plays,
            "Play history cascaded on game deletion"
        )
        
    def test_tags_storage(self):
        """Test tag storage and retrieval."""
        print("\n[7] Testing Tags Storage")
        print("-" * 50)
        
        # Add game with tags
        game_id = self.tracker.add_game(
            name="Tagged Game",
            min_players=1,
            max_players=4,
            tags=["horror", "co-op", "survival"]
        )
        
        self.assert_test(
            game_id is not None,
            "Added game with tags"
        )
        
        # Retrieve and verify tags
        game = self.tracker.get_game_by_name("Tagged Game")
        if game:
            self.assert_test(
                isinstance(game['tags'], list),
                "Tags retrieved as list"
            )
            self.assert_test(
                len(game['tags']) == 3,
                f"All tags present (expected 3, got {len(game['tags'])})"
            )
            self.assert_test(
                "horror" in game['tags'],
                "Tag content preserved"
            )
        else:
            self.assert_test(False, "Could not retrieve tagged game")
            
    def test_database_stats(self):
        """Test database statistics."""
        print("\n[8] Testing Database Statistics")
        print("-" * 50)
        
        stats = self.tracker.get_stats()
        
        self.assert_test(
            'total_games' in stats,
            "Stats include game count"
        )
        self.assert_test(
            'total_plays' in stats,
            "Stats include play count"
        )
        self.assert_test(
            'total_suggestions' in stats,
            "Stats include suggestion count"
        )
        self.assert_test(
            stats['total_games'] > 0,
            "Games were recorded"
        )
        
    def run_all_tests(self):
        """Run all database tests."""
        print("\n" + "=" * 50)
        print("Mitch Database Testing Utility")
        print("=" * 50)
        
        try:
            self.setup()
            
            self.test_database_init()
            self.test_add_games()
            self.test_query_games()
            self.test_play_history()
            self.test_suggestions()
            self.test_foreign_keys()
            self.test_tags_storage()
            self.test_database_stats()
            
        finally:
            self.cleanup()
        
        # Print summary
        print("\n" + "=" * 50)
        print("Test Results:")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print("=" * 50)
        
        if self.failed == 0:
            print("\n✓ All database tests passed!\n")
            return 0
        else:
            print(f"\n✗ {self.failed} test(s) failed.\n")
            return 1


def main():
    """Main test entry point."""
    tester = DatabaseTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
