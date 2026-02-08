"""
Suggestion Engine - Smart game recommendation system for Mitch

Combines game database queries with AI reasoning to suggest appropriate games
based on player count, recent play history, and cooldown periods.
"""

import logging
import random
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """
    Generates smart game suggestions based on context and history.
    
    Combines database knowledge with AI reasoning to suggest appropriate games.
    """
    
    def __init__(self, game_tracker, personality, config):
        """
        Initialize suggestion engine.
        
        Args:
            game_tracker: GameTracker instance for database access
            personality: PersonalitySystem instance for AI responses
            config: Bot configuration dict
        """
        self.game_tracker = game_tracker
        self.personality = personality
        self.config = config
        
        # Load suggestion settings from config
        suggestion_config = config.get('suggestions', {})
        self.cooldown_hours = suggestion_config.get('cooldown_hours', 48)
        self.max_suggestions = suggestion_config.get('max_suggestions', 3)
        self.recent_plays_window = suggestion_config.get('recent_plays_window', 7)
        
        logger.info(
            f"SuggestionEngine initialized: "
            f"cooldown={self.cooldown_hours}h, "
            f"max_suggestions={self.max_suggestions}"
        )
    
    async def suggest_games(
        self,
        player_count: int,
        requester_name: Optional[str] = None
    ) -> str:
        """
        Generate game suggestions for given player count.
        
        This is the main entry point for generating suggestions.
        
        Args:
            player_count: Number of players (int)
            requester_name: Name of person asking (optional)
            
        Returns:
            str: AI-generated suggestion text
        """
        logger.info(
            f"Generating suggestion for {player_count} players "
            f"(requested by {requester_name or 'unknown'})"
        )
        
        # Check if game library is empty
        all_games = self.game_tracker.get_all_games()
        if not all_games:
            logger.warning("Game library is empty")
            return (
                "hey your game library is empty! "
                "run 'python3 scripts/setup_games.py populate' to add some games"
            )
        
        # Filter games by player count and cooldown
        filtered_games = self._filter_games(player_count, self.cooldown_hours)
        
        logger.info(f"Filtered to {len(filtered_games)} games after cooldown")
        
        # If no games available after filtering, relax cooldown
        if not filtered_games:
            logger.info("No games available after cooldown, relaxing restrictions")
            filtered_games = self._get_least_recent_games(player_count)
            
            if not filtered_games:
                # Still no games? Player count might not match anything
                return self._handle_no_matching_games(player_count)
        
        # Build context for AI
        context = self._build_context(
            filtered_games,
            player_count,
            requester_name
        )
        
        # Build prompt for AI
        prompt = self._build_prompt(context)
        
        logger.debug(f"Built prompt: {prompt[:200]}...")
        
        # Generate AI response with fallback
        try:
            response = await self.personality.generate_response(
                user_message=prompt,
                context=context
            )
            
            # Record suggestions in database
            self._record_suggestions(response, filtered_games, context)
            
            return response
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}", exc_info=True)
            # Fallback: simple random suggestion
            return self._generate_fallback_suggestion(filtered_games)
    
    def _filter_games(
        self,
        player_count: int,
        cooldown_hours: int
    ) -> List[Dict[str, Any]]:
        """
        Filter games by player count and cooldown period.
        
        Args:
            player_count: Number of players
            cooldown_hours: Hours since last play to exclude games
            
        Returns:
            list: Filtered games that are good suggestions
        """
        # Get all games that support this player count
        matching_games = self.game_tracker.get_games_for_players(player_count)
        
        if not matching_games:
            logger.warning(f"No games support {player_count} players")
            return []
        
        logger.debug(f"Found {len(matching_games)} games for {player_count} players")
        
        # Get recent plays within cooldown window
        # Calculate hours as days for recent_plays query (convert hours to days)
        days_back = max(int(cooldown_hours / 24) + 1, self.recent_plays_window)
        recent_plays = self.game_tracker.get_recent_plays(days=days_back)
        
        # Build set of game IDs played within cooldown period
        cooldown_cutoff = datetime.now() - timedelta(hours=cooldown_hours)
        recent_game_ids = set()
        
        for play in recent_plays:
            # Parse played_date string to datetime
            played_date = datetime.fromisoformat(play['played_date'].replace('Z', '+00:00'))
            if played_date > cooldown_cutoff:
                recent_game_ids.add(play['game_id'])
        
        logger.debug(
            f"Found {len(recent_game_ids)} games played within "
            f"{cooldown_hours}h cooldown"
        )
        
        # Filter out recently played games
        filtered = [
            game for game in matching_games
            if game['id'] not in recent_game_ids
        ]
        
        return filtered
    
    def _get_least_recent_games(self, player_count: int) -> List[Dict[str, Any]]:
        """
        Get least recently played games when cooldown filters out everything.
        
        Args:
            player_count: Number of players
            
        Returns:
            list: Games sorted by last played (least recent first)
        """
        # Get all games for player count
        matching_games = self.game_tracker.get_games_for_players(player_count)
        
        if not matching_games:
            return []
        
        # Get play history to find when each was last played
        recent_plays = self.game_tracker.get_recent_plays(days=90)  # Look back 90 days
        
        # Build map of game_id -> most recent play date
        last_played = {}
        for play in recent_plays:
            game_id = play['game_id']
            played_date = datetime.fromisoformat(play['played_date'].replace('Z', '+00:00'))
            
            if game_id not in last_played or played_date > last_played[game_id]:
                last_played[game_id] = played_date
        
        # Sort games by last played date (oldest first)
        # Games never played get a very old date
        never_played_date = datetime.min
        sorted_games = sorted(
            matching_games,
            key=lambda g: last_played.get(g['id'], never_played_date)
        )
        
        # Return top N least recent
        return sorted_games[:self.max_suggestions]
    
    def _handle_no_matching_games(self, player_count: int) -> str:
        """
        Generate message when no games match player count.
        
        Args:
            player_count: Requested player count
            
        Returns:
            str: Friendly message about available player counts
        """
        # Get all games to see what player counts are available
        all_games = self.game_tracker.get_all_games()
        
        if not all_games:
            return "hmm, game library seems empty"
        
        # Find nearby player counts that have games
        nearby_counts = set()
        for game in all_games:
            if game['min_players'] <= player_count + 2 and game['max_players'] >= player_count - 2:
                nearby_counts.add(f"{game['min_players']}-{game['max_players']}")
        
        if nearby_counts:
            counts_str = ", ".join(sorted(nearby_counts)[:3])
            return f"hmm, no games for exactly {player_count} players. got games for {counts_str} though"
        
        return f"don't have many games for {player_count} people"
    
    def _build_context(
        self,
        filtered_games: List[Dict[str, Any]],
        player_count: int,
        requester_name: Optional[str]
    ) -> Dict[str, Any]:
        """
        Build rich context for AI prompt.
        
        Args:
            filtered_games: List of game dicts after filtering
            player_count: Number of players
            requester_name: Person asking (optional)
            
        Returns:
            dict: Context dictionary for AI
        """
        # Get recent plays for context
        recent_plays = self.game_tracker.get_recent_plays(days=self.recent_plays_window)
        
        # Build recent plays summary (most recent first, limited)
        recent_summary = []
        for play in recent_plays[:5]:  # Top 5 most recent
            played_date = datetime.fromisoformat(play['played_date'].replace('Z', '+00:00'))
            days_ago = (datetime.now() - played_date).days
            
            if days_ago == 0:
                when = "today"
            elif days_ago == 1:
                when = "yesterday"
            else:
                when = f"{days_ago} days ago"
            
            recent_summary.append({
                "name": play['game_name'],
                "when": when
            })
        
        context = {
            "player_count": player_count,
            "filtered_games": [
                {
                    "name": g['name'],
                    "category": g['category'] or "misc",
                    "min_players": g['min_players'],
                    "max_players": g['max_players']
                }
                for g in filtered_games[:10]  # Limit to keep prompt size down
            ],
            "recent_plays": recent_summary,
            "requester": requester_name,
            "total_games_in_library": len(self.game_tracker.get_all_games()),
            "cooldown_hours": self.cooldown_hours
        }
        
        return context
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build complete prompt for AI including context.
        
        This creates a focused prompt that guides the AI to suggest
        games from the available list while maintaining Mitch's personality.
        
        Args:
            context: Context dict from _build_context
            
        Returns:
            str: Complete prompt ready for AI
        """
        player_count = context['player_count']
        filtered_games = context['filtered_games']
        recent_plays = context['recent_plays']
        
        # Build game list string - just names, no extra info
        game_names = [g['name'] for g in filtered_games]
        games_str = ", ".join(game_names[:6])  # Top 6 to keep prompt short
        
        if len(game_names) > 6:
            games_str += f" (and {len(game_names) - 6} more)"
        
        # Build recent plays string
        if recent_plays:
            recent_str = ", ".join([
                f"{p['name']} ({p['when']})" 
                for p in recent_plays[:3]
            ])
        else:
            recent_str = "nothing recently"
        
        # Build a very strict prompt that forces casual style
        prompt = f"""you're mitch. someone asks what to play.

{player_count} people online
games available: {games_str}
recently played: {recent_str}

pick 1-2 games from available list. be super casual. under 150 chars. no formal language.

examples of good responses:
"how about Deep Rock Galactic?"
"maybe Phasmophobia or Lethal Company"
"try Valheim, haven't played that in a bit"

examples of BAD responses (never do this):
"I'd recommend..."
"hey [name], based on..."
"checking out..."

respond:"""
        
        return prompt
    
    def _record_suggestions(
        self,
        response: str,
        candidate_games: List[Dict[str, Any]],
        context: Dict[str, Any]
    ):
        """
        Record suggested games in database for analytics.
        
        Attempts to parse game names from AI response and record them.
        Best-effort approach - doesn't fail if parsing fails.
        
        Args:
            response: AI-generated response text
            candidate_games: Games that could have been suggested
            context: Context used for suggestion
        """
        try:
            # Extract game names mentioned in response
            suggested_games = self._extract_game_names(response, candidate_games)
            
            logger.info(f"Recording {len(suggested_games)} suggestions")
            
            # Record each suggestion
            for game_name in suggested_games:
                game = self.game_tracker.get_game_by_name(game_name)
                if game:
                    context_json = json.dumps({
                        "player_count": context['player_count'],
                        "requester": context.get('requester'),
                        "filtered_count": len(candidate_games)
                    })
                    
                    self.game_tracker.record_suggestion(
                        game_id=game['id'],
                        context=context_json
                    )
            
        except Exception as e:
            logger.warning(f"Failed to record suggestions: {e}")
            # Don't fail the whole suggestion if recording fails
    
    def _extract_game_names(
        self,
        ai_response: str,
        candidate_games: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract mentioned game names from AI response.
        
        Uses best-effort string matching against candidate games.
        
        Args:
            ai_response: AI generated text
            candidate_games: List of game dicts that could be mentioned
            
        Returns:
            list: Game names found in response
        """
        found_games = []
        response_lower = ai_response.lower()
        
        for game in candidate_games:
            game_name_lower = game['name'].lower()
            
            # Check if game name appears in response
            if game_name_lower in response_lower:
                found_games.append(game['name'])
        
        return found_games
    
    def _generate_fallback_suggestion(
        self,
        filtered_games: List[Dict[str, Any]]
    ) -> str:
        """
        Generate simple fallback suggestion if AI fails.
        
        Picks a random game from filtered list and formats a basic message.
        
        Args:
            filtered_games: List of available games
            
        Returns:
            str: Simple suggestion message
        """
        if not filtered_games:
            return "hmm not sure what to suggest right now"
        
        # Pick random game
        game = random.choice(filtered_games[:5])  # Top 5 to prefer better matches
        
        # Simple casual suggestion
        suggestions = [
            f"how about {game['name']}?",
            f"maybe {game['name']}",
            f"{game['name']} could be good",
            f"try {game['name']}?"
        ]
        
        return random.choice(suggestions)
