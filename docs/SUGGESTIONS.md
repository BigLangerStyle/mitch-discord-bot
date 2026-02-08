# How Mitch's Suggestions Work

This document explains the algorithm and logic behind Mitch's game suggestions.

## Overview

When you ask "what should we play?", Mitch combines three things:
1. **Database knowledge** - What games are in the library, player counts, recent plays
2. **Intelligent filtering** - Remove games played recently, match player count
3. **AI reasoning** - Pick 1-2 games and explain why in Mitch's casual style

## The Algorithm

### Step 1: Detect Suggestion Request

Bot detects if the user wants a game suggestion by checking for keywords:
- "what should we play"
- "what should i play"
- "game suggestion"
- "recommend a game"
- "what game"

If keywords aren't found, treats it as casual conversation instead.

### Step 2: Estimate Player Count

Bot looks at Discord server context to estimate player count:
- Counts online members (excluding bots)
- Defaults to 4 if count is unclear
- Caps at 10 (max supported by most games)

**Future enhancement:** Could check voice channels, parse message for explicit count.

### Step 3: Filter Games by Player Count

Query database for games where:
```
min_players <= player_count <= max_players
```

Example: 4 players → includes games with ranges like 2-6, 1-8, 4-4, etc.

### Step 4: Apply Cooldown Period

Remove recently played games from suggestions:
- Default cooldown: **48 hours** (configurable)
- Queries play history table for games played within cooldown window
- Filters out those game IDs from available suggestions

**If no games remain after cooldown:**
- Relaxes cooldown restriction
- Suggests least recently played games instead
- This prevents "no suggestions available" when everything was played

### Step 5: Build Context for AI

Creates a rich context dictionary with:
```python
{
    "player_count": 4,
    "filtered_games": [
        {"name": "Deep Rock Galactic", "category": "co-op"},
        {"name": "Overcooked 2", "category": "party"}
    ],
    "recent_plays": [
        {"name": "Valheim", "when": "yesterday"},
        {"name": "Among Us", "when": "3 days ago"}
    ],
    "requester": "Alice"
}
```

### Step 6: Build AI Prompt

Constructs a focused prompt for the AI:
```
helping decide what to play

context:
- 4 players
- available: Deep Rock Galactic, Overcooked 2, Phasmophobia
- recently played: Valheim (yesterday), Among Us (3 days ago)
- asking: Alice

suggest 1-2 games from the available list. be brief and casual. 
consider variety from recent plays. under 200 chars.
```

### Step 7: Generate AI Response

- Sends prompt to Ollama (local phi3:mini model)
- AI picks 1-2 games from the available list
- Response is polished to remove corporate language
- Falls back to simple random suggestion if AI fails

### Step 8: Record Suggestion

Parses AI response to extract mentioned game names and records in database:
```sql
INSERT INTO suggestions (game_id, context)
VALUES (game_id, '{"player_count": 4, "requester": "Alice"}')
```

Used for analytics: suggestion acceptance rate, most suggested games, etc.

## Configuration

All settings in `config/config.yaml`:

```yaml
suggestions:
  # How many days of play history to consider
  recent_plays_window: 7
  
  # Minimum hours before suggesting same game again
  cooldown_hours: 48
  
  # Maximum number of suggestions to provide
  max_suggestions: 3
  
  # Include player count in context
  use_player_count: true
```

## Examples

### Normal Suggestion
```
User: @Mitch what should we play?

[4 players online, library has 10 games]
[Filter: 7 games support 4 players]
[Cooldown: 2 recently played, 5 remain]
[AI picks: Deep Rock Galactic]

Mitch: "how about Deep Rock Galactic? you guys haven't touched that in a while"
```

### All Games in Cooldown
```
User: @Mitch game suggestion?

[4 players online]
[Filter: 5 games support 4 players]
[Cooldown: All 5 played in last 48h]
[Relax cooldown: Pick least recent = Overcooked 2 (3 days ago)]

Mitch: "hmm tough call, all your 4-player games were played recently. 
how about revisiting Overcooked 2?"
```

### No Matching Games
```
User: @Mitch what should we play?

[7 players online]
[Filter: 0 games support 7 players]
[Check nearby: Games for 4-6 and 8-10 exist]

Mitch: "hmm, no games for exactly 7 players. got games for 4-6, 8-10 though"
```

### Empty Library
```
User: @Mitch recommend something

[0 games in database]

Mitch: "hey your game library is empty! run the setup script to add some games"
```

## Edge Cases & Fallbacks

### AI Timeout or Failure
If Ollama takes too long or fails:
1. Log the error
2. Pick random game from filtered list
3. Generate simple message: "how about {game}?"

### Invalid Player Count
If player count detection fails:
- Default to 4 players (reasonable average)
- Log warning for debugging

### No Games Match Filters
If filters are too strict:
1. Check nearby player counts
2. Suggest widening criteria
3. Or suggest games that are close

### Database Connection Issues
If database query fails:
- Fall back to hardcoded suggestions
- Log error for investigation
- Bot continues running (doesn't crash)

## Performance Characteristics

**Database queries:** Fast (<10ms)
- Indexed on player count and dates
- Small dataset (typically <100 games, <1000 plays)

**AI generation:** Moderate (3-20s)
- Depends on server CPU
- Uses async to not block Discord bot
- Timeout set to 60s

**Total response time:** Usually 3-15 seconds
- Acceptable for Discord chat
- Shows typing indicator while processing

## Testing

Test suggestions without Discord:
```bash
python scripts/test_suggestions.py
```

Interactive prompts:
- Enter player count to test suggestion
- Shows filtered games before AI response
- Displays response time
- Can record plays to test cooldown

## Future Enhancements

Possible improvements (not yet implemented):

1. **Voice Channel Detection**
   - Check who's in voice channels first
   - More accurate than counting online members

2. **Parse Message for Count**
   - "for 3 people" → use 3 instead of estimation
   - "me and Bob" → use 2

3. **Category Preferences**
   - "suggest a co-op game"
   - "something competitive"

4. **Time-based Suggestions**
   - Quick games in evening
   - Long campaigns on weekends

5. **Reaction Tracking**
   - React ✅ to suggestion if you play it
   - Improves suggestion accuracy analytics

6. **Machine Learning**
   - Learn group preferences over time
   - Weight suggestions by past acceptance

## Troubleshooting

**"game library is empty"**
→ Run: `python scripts/setup_games.py populate`

**Suggestions seem random/bad**
→ Check cooldown setting in config (may be too aggressive)
→ Check if play history is being recorded properly

**AI takes forever**
→ Normal on slower CPUs (MediaServer is fine)
→ Check Ollama is running: `ollama serve`
→ Verify model downloaded: `ollama pull phi3:mini`

**Same games suggested repeatedly**
→ Check if play history is being recorded
→ Reduce cooldown_hours in config
→ Add more games to library

**Bot crashes on suggestion**
→ Check logs: `tail -f data/mitch.log`
→ Verify database exists and has write permissions
→ Test suggestion engine: `python scripts/test_suggestions.py`

## Analytics Queries

Get suggestion statistics:
```python
from src.game_tracker import GameTracker
tracker = GameTracker()
stats = tracker.get_suggestion_stats()
print(stats)
```

Find most suggested games:
```sql
SELECT g.name, COUNT(*) as suggestion_count
FROM suggestions s
JOIN games g ON s.game_id = g.id
GROUP BY g.id
ORDER BY suggestion_count DESC
LIMIT 10;
```

Find acceptance rate by game:
```sql
SELECT 
    g.name,
    COUNT(*) as suggestions,
    SUM(s.accepted) as accepted,
    ROUND(100.0 * SUM(s.accepted) / COUNT(*), 1) as acceptance_rate
FROM suggestions s
JOIN games g ON s.game_id = g.id
GROUP BY g.id
HAVING COUNT(*) >= 3
ORDER BY acceptance_rate DESC;
```
