"""
Game Tracker - Database operations for Mitch Discord Bot

Manages the game library, play history, and suggestion tracking using SQLite.
Handles all database operations including queries, inserts, and updates.

Database Schema:
- games: Game library with player counts and categories
- play_history: Record of when games were played
- suggestions: Track what Mitch suggested for analytics
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GameTracker:
    """Manages game library and play history in SQLite database."""
    
    def __init__(self, db_path: str = 'data/mitch.db', config: Optional[Dict] = None):
        """
        Initialize database connection and create tables.
        
        Args:
            db_path: Path to SQLite database file
            config: Optional config dict with database settings
        """
        # Use config if provided, otherwise use default
        if config and 'database' in config:
            self.db_path = config['database'].get('path', db_path)
        else:
            self.db_path = db_path
            
        # Ensure data directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing GameTracker with database: {self.db_path}")
        
        # Initialize database and create tables
        self.init_db()
        
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a new database connection with proper settings.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        
        # Enable foreign keys (must be set for every connection)
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Use WAL mode for better concurrency (only needs to be set once)
        conn.execute("PRAGMA journal_mode = WAL")
        
        return conn
        
    def init_db(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Games table - stores game library
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    min_players INTEGER DEFAULT 1,
                    max_players INTEGER DEFAULT 10,
                    category TEXT,
                    tags TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Play history table - tracks when games are played
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS play_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    played_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    player_count INTEGER,
                    notes TEXT,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
            """)
            
            # Suggestions table - tracks what Mitch suggested
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    suggested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    context TEXT,
                    accepted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_players 
                ON games(min_players, max_players)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_play_history_date 
                ON play_history(played_date)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_suggestions_date 
                ON suggestions(suggested_date)
            """)
            
            conn.commit()
            logger.info("Database tables and indexes created successfully")
            
    def add_game(
        self,
        name: str,
        min_players: int = 1,
        max_players: int = 10,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Add a game to the library.
        
        Args:
            name: Game name
            min_players: Minimum player count
            max_players: Maximum player count
            category: Game category (e.g., "co-op", "party", "competitive")
            tags: List of tags (e.g., ["horror", "survival"])
            
        Returns:
            Game ID if successful, None if game already exists
        """
        # Convert tags list to JSON string
        tags_json = json.dumps(tags) if tags else None
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO games (name, min_players, max_players, category, tags)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (name, min_players, max_players, category, tags_json)
                )
                conn.commit()
                game_id = cursor.lastrowid
                logger.info(f"Added game: {name} (ID: {game_id})")
                return game_id
                
        except sqlite3.IntegrityError:
            logger.warning(f"Game '{name}' already exists in library")
            return None
            
    def get_all_games(self) -> List[Dict[str, Any]]:
        """
        Get all games in the library.
        
        Returns:
            List of game dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, min_players, max_players, category, tags, added_date
                FROM games
                ORDER BY name
            """)
            
            games = []
            for row in cursor.fetchall():
                game = dict(row)
                # Parse tags JSON back to list
                if game['tags']:
                    game['tags'] = json.loads(game['tags'])
                else:
                    game['tags'] = []
                games.append(game)
                
            return games
            
    def get_games_for_players(self, player_count: int) -> List[Dict[str, Any]]:
        """
        Get games that support the given player count.
        
        Args:
            player_count: Number of players
            
        Returns:
            List of game dictionaries that support this player count
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, min_players, max_players, category, tags
                FROM games
                WHERE min_players <= ? AND max_players >= ?
                ORDER BY name
            """, (player_count, player_count))
            
            games = []
            for row in cursor.fetchall():
                game = dict(row)
                # Parse tags JSON back to list
                if game['tags']:
                    game['tags'] = json.loads(game['tags'])
                else:
                    game['tags'] = []
                games.append(game)
                
            logger.debug(f"Found {len(games)} games for {player_count} players")
            return games
            
    def get_game_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a game by name (case-insensitive).
        
        Args:
            name: Game name to search for
            
        Returns:
            Game dictionary if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, min_players, max_players, category, tags, added_date
                FROM games
                WHERE LOWER(name) = LOWER(?)
            """, (name,))
            
            row = cursor.fetchone()
            if row:
                game = dict(row)
                # Parse tags JSON back to list
                if game['tags']:
                    game['tags'] = json.loads(game['tags'])
                else:
                    game['tags'] = []
                return game
            return None
            
    def get_game_by_id(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a game by its ID.
        
        Args:
            game_id: Game ID
            
        Returns:
            Game dictionary if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, min_players, max_players, category, tags, added_date
                FROM games
                WHERE id = ?
            """, (game_id,))
            
            row = cursor.fetchone()
            if row:
                game = dict(row)
                # Parse tags JSON back to list
                if game['tags']:
                    game['tags'] = json.loads(game['tags'])
                else:
                    game['tags'] = []
                return game
            return None
            
    def record_play(
        self,
        game_id: int,
        player_count: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Record that a game was played.
        
        Args:
            game_id: ID of the game that was played
            player_count: Number of players (optional)
            notes: Additional notes (optional)
            
        Returns:
            Play history ID if successful, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO play_history (game_id, player_count, notes)
                    VALUES (?, ?, ?)
                """, (game_id, player_count, notes))
                conn.commit()
                
                play_id = cursor.lastrowid
                game = self.get_game_by_id(game_id)
                game_name = game['name'] if game else f"ID {game_id}"
                logger.info(f"Recorded play: {game_name} (Play ID: {play_id})")
                return play_id
                
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to record play for game_id {game_id}: {e}")
            return None
            
    def get_recent_plays(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get games played in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of play history dictionaries with game info
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.id,
                    p.game_id,
                    p.played_date,
                    p.player_count,
                    p.notes,
                    g.name as game_name,
                    g.category,
                    g.tags
                FROM play_history p
                JOIN games g ON p.game_id = g.id
                WHERE p.played_date >= datetime('now', ? || ' days')
                ORDER BY p.played_date DESC
            """, (f'-{days}',))
            
            plays = []
            for row in cursor.fetchall():
                play = dict(row)
                # Parse tags JSON back to list
                if play['tags']:
                    play['tags'] = json.loads(play['tags'])
                else:
                    play['tags'] = []
                plays.append(play)
                
            logger.debug(f"Found {len(plays)} plays in last {days} days")
            return plays
            
    def record_suggestion(
        self,
        game_id: Optional[int],
        context: Optional[str] = None
    ) -> Optional[int]:
        """
        Record that a game was suggested by Mitch.
        
        Args:
            game_id: ID of suggested game (None if suggestion was generic)
            context: Context of the suggestion (player count, etc.)
            
        Returns:
            Suggestion ID if successful, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO suggestions (game_id, context)
                    VALUES (?, ?)
                """, (game_id, context))
                conn.commit()
                
                suggestion_id = cursor.lastrowid
                if game_id:
                    game = self.get_game_by_id(game_id)
                    game_name = game['name'] if game else f"ID {game_id}"
                    logger.debug(f"Recorded suggestion: {game_name}")
                else:
                    logger.debug("Recorded generic suggestion")
                    
                return suggestion_id
                
        except Exception as e:
            logger.error(f"Failed to record suggestion: {e}")
            return None
            
    def mark_suggestion_accepted(self, suggestion_id: int) -> bool:
        """
        Mark a suggestion as accepted (game was played after suggestion).
        
        Args:
            suggestion_id: ID of the suggestion
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE suggestions
                    SET accepted = 1
                    WHERE id = ?
                """, (suggestion_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.debug(f"Marked suggestion {suggestion_id} as accepted")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to mark suggestion as accepted: {e}")
            return False
            
    def get_suggestion_stats(self) -> Dict[str, Any]:
        """
        Get statistics about suggestions for analytics.
        
        Returns:
            Dictionary with suggestion statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total suggestions
            cursor.execute("SELECT COUNT(*) as total FROM suggestions")
            total = cursor.fetchone()['total']
            
            # Accepted suggestions
            cursor.execute("SELECT COUNT(*) as accepted FROM suggestions WHERE accepted = 1")
            accepted = cursor.fetchone()['accepted']
            
            # Recent suggestions (last 30 days)
            cursor.execute("""
                SELECT COUNT(*) as recent 
                FROM suggestions 
                WHERE suggested_date >= datetime('now', '-30 days')
            """)
            recent = cursor.fetchone()['recent']
            
            # Most suggested games
            cursor.execute("""
                SELECT 
                    g.name,
                    COUNT(*) as suggestion_count
                FROM suggestions s
                JOIN games g ON s.game_id = g.id
                GROUP BY g.name
                ORDER BY suggestion_count DESC
                LIMIT 5
            """)
            top_games = [dict(row) for row in cursor.fetchall()]
            
            acceptance_rate = (accepted / total * 100) if total > 0 else 0
            
            return {
                'total_suggestions': total,
                'accepted_suggestions': accepted,
                'acceptance_rate': round(acceptance_rate, 2),
                'recent_suggestions': recent,
                'top_suggested_games': top_games
            }
            
    def delete_game(self, game_id: int) -> bool:
        """
        Delete a game from the library.
        Note: This will cascade delete play history and set suggestions to NULL.
        
        Args:
            game_id: ID of game to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Deleted game ID {game_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete game {game_id}: {e}")
            return False
            
    def clear_all_games(self) -> bool:
        """
        Clear all games from the library.
        WARNING: This will delete all games, play history, and suggestions!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete in correct order due to foreign keys
                cursor.execute("DELETE FROM suggestions")
                cursor.execute("DELETE FROM play_history")
                cursor.execute("DELETE FROM games")
                
                conn.commit()
                logger.warning("Cleared all games, play history, and suggestions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear games: {e}")
            return False
            
    def get_stats(self) -> Dict[str, int]:
        """
        Get overall database statistics.
        
        Returns:
            Dictionary with counts of games, plays, and suggestions
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM games")
            game_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM play_history")
            play_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM suggestions")
            suggestion_count = cursor.fetchone()['count']
            
            return {
                'total_games': game_count,
                'total_plays': play_count,
                'total_suggestions': suggestion_count
            }
            
    def close(self):
        """
        Close database connection.
        Note: Using context managers means connections auto-close,
        but this method is here for explicit cleanup if needed.
        """
        # With our current implementation using context managers,
        # connections are automatically closed after each operation.
        # This method exists for API compatibility.
        logger.debug("GameTracker close() called (connections auto-managed)")
        pass


# Convenience function for quick database access
def get_tracker(config: Optional[Dict] = None) -> GameTracker:
    """
    Get a GameTracker instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        GameTracker instance
    """
    return GameTracker(config=config)
