# Mitch Architecture Overview

**Version:** 1.2.0  
**Last Updated:** February 2026

This document explains how Mitch's components work together to create a natural, AI-powered gaming companion bot.

---

## Table of Contents

- [High-Level Overview](#high-level-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Database Schema](#database-schema)
- [Configuration System](#configuration-system)
- [Error Handling Strategy](#error-handling-strategy)
- [Performance Considerations](#performance-considerations)

---

## High-Level Overview

Mitch is built with a modular architecture where each component has a single, well-defined responsibility:

```
┌─────────────────────────────────────────────────────────────┐
│                      Discord Bot (bot.py)                    │
│  • Event handling (on_ready, on_message)                    │
│  • @mention detection                                       │
│  • Message routing (casual vs suggestion)                   │
│  • Conversation context tracking                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  Router Decision: Game Request?    │
         └────────────────────────────────────┘
                 │                    │
         YES (game request)    NO (casual chat)
                 │                    │
                 ▼                    ▼
    ┌────────────────────┐  ┌──────────────────────┐
    │ Suggestion Engine  │  │ Casual Response      │
    │ (suggestion_       │  │ (personality.py)     │
    │  engine.py)        │  │                      │
    │                    │  │ • Build chat prompt  │
    │ • Filter games     │  │ • Add conversation   │
    │ • Apply cooldowns  │  │   context            │
    │ • Build context    │  │ • Light polishing    │
    └────────────────────┘  └──────────────────────┘
                 │                    │
                 ▼                    │
    ┌────────────────────┐           │
    │ Game Tracker       │           │
    │ (game_tracker.py)  │           │
    │                    │           │
    │ • Query games      │           │
    │ • Check history    │           │
    │ • Record plays     │           │
    └────────────────────┘           │
                 │                    │
                 ▼                    │
    ┌────────────────────┐           │
    │ Personality System │◄──────────┘
    │ (personality.py)   │
    │                    │
    │ • Build AI prompt  │
    │ • Add game context │
    │ • Strict polishing │
    └────────────────────┘
                 │
                 ▼
    ┌────────────────────┐
    │  Ollama Client     │
    │  (ollama_client.py)│
    │                    │
    │ • HTTP API call    │
    │ • Timeout handling │
    │ • Error recovery   │
    └────────────────────┘
                 │
                 ▼
    ┌────────────────────┐
    │  Local Ollama      │
    │  (phi3:mini)       │
    │                    │
    │ • AI inference     │
    │ • Response gen     │
    └────────────────────┘
```

---

## Component Architecture

### 1. Discord Bot (`src/bot.py`)

**Responsibility:** Entry point and Discord event handling

**Key Functions:**
- `on_ready()` - Initialization, logging bot startup
- `on_message(message)` - Main message handler
- `should_respond(message)` - @mention detection
- `is_game_request(content)` - Route to suggestion engine or casual chat
- `get_conversation_context(channel, limit)` - Fetch recent messages for context

**Design Decisions:**
- Uses flexible keyword matching (not rigid phrases) to detect game requests
- Tracks conversation context per channel (last 5 messages by default)
- Optional rate limiting to prevent spam (disabled by default for friend groups)
- Graceful error handling - bot never crashes on bad input

**Dependencies:**
- `discord.py` - Discord API
- `suggestion_engine` - Game recommendations
- `personality` - Response generation
- `config_loader` - Configuration

---

### 2. Suggestion Engine (`src/suggestion_engine.py`)

**Responsibility:** Smart game recommendation logic

**Key Functions:**
- `get_suggestion(player_count)` - Main entry point
- `_filter_games_by_player_count(player_count)` - Query database for compatible games
- `_filter_by_cooldown(games)` - Remove recently played games
- `_build_suggestion_context(games, player_count)` - Create AI prompt
- `_record_suggestion(game_name, player_count)` - Log suggestion for analytics

**Algorithm:**
1. **Player Count Detection** - Counts online members in Discord server
2. **Database Filtering** - Queries games that support player count
3. **Cooldown Check** - Removes games played in last 48 hours (configurable)
4. **Context Building** - Creates prompt with available games + recent history
5. **AI Generation** - Calls personality system for natural suggestion
6. **Recording** - Saves suggestion to database

**Fallback Strategy:**
- If no games pass cooldown → Suggest least recently played
- If database empty → Direct user to populate library
- If AI fails → Return simple text fallback

**Dependencies:**
- `game_tracker` - Database operations
- `personality` - AI response generation
- `ollama_client` - Indirectly through personality

---

### 3. Personality System (`src/personality.py`)

**Responsibility:** AI prompt construction and response polishing

**Key Functions:**
- `get_suggestion_response(context, config)` - Game suggestion prompts (strict polish)
- `get_casual_response(user_message, context, config)` - Casual chat prompts (light polish)
- `_build_system_prompt(context_type)` - Core personality definition
- `_polish_response(response, strict)` - Clean up AI output
- `_add_conversation_context(messages)` - Format recent chat for AI

**Personality Traits:**
- **Casual gaming buddy** - Not a corporate assistant
- **Brief responses** - Under 300 chars for chat, under 500 for suggestions
- **Gaming slang** - "ggs", "lol", "what's the vibe"
- **Honest** - Admits uncertainty, doesn't pretend to know
- **No emojis** - Clean text responses

**Two Polishing Modes:**
- **Light Polish** (casual chat) - Removes excessive punctuation, corporate language
- **Strict Polish** (suggestions) - Also removes emojis, fixes capitalization

**System Prompts:**
- Suggestion: "You're Mitch, a casual gaming buddy helping friends pick games..."
- Casual: "You're Mitch, a chill gaming buddy chatting with friends..."

**Dependencies:**
- `ollama_client` - AI inference
- `config` - Temperature, max_tokens, etc.

---

### 4. Ollama Client (`src/ollama_client.py`)

**Responsibility:** HTTP communication with local Ollama instance

**Key Functions:**
- `generate(prompt, system_prompt, config)` - Main API call
- `_build_request_payload(prompt, system, config)` - Construct JSON payload
- `_handle_timeout()` - Graceful timeout handling
- `_handle_connection_error()` - Network error recovery

**Configuration:**
- **Host:** `http://localhost:11434` (configurable)
- **Model:** `phi3:mini` (lightweight, CPU-friendly)
- **Temperature:** `0.8` (balanced creativity)
- **Max Tokens:** `300` (concise responses)
- **Timeout:** `60s` (can be increased for slower hardware)

**Error Handling:**
- Connection failures → Log error, return None
- Timeouts → Log warning, return None
- Invalid responses → Log error, return None
- Caller must handle None responses with fallbacks

**Dependencies:**
- `aiohttp` - Async HTTP client (from discord.py)
- `ollama` service running locally

---

### 5. Game Tracker (`src/game_tracker.py`)

**Responsibility:** SQLite database operations

**Key Functions:**
- `get_games_for_player_count(player_count)` - Query compatible games
- `get_recent_plays(days)` - Fetch play history
- `record_play(game_name)` - Mark game as played
- `record_suggestion(game_name, player_count, response)` - Log AI suggestions
- `add_game(name, min_p, max_p, category)` - Add game to library
- `get_all_games()` - List entire library
- `clear_library()` - Remove all games

**Database Schema:** See [Database Schema](#database-schema) below

**Design Decisions:**
- WAL mode for better concurrency
- Foreign key constraints enforced
- Context managers for connection safety
- Graceful handling of constraint violations

**Dependencies:**
- `sqlite3` - Python standard library
- `config` - Database path and settings

---

### 6. Config Loader (`src/config_loader.py`)

**Responsibility:** YAML configuration parsing

**Key Functions:**
- `load_config(path)` - Parse config.yaml
- `validate_config(config)` - Ensure required fields exist
- `get_nested_value(config, keys)` - Safe nested access

**Validation:**
- Checks for required fields (discord.token, ollama.host, etc.)
- Provides default values for optional settings
- Raises clear errors for missing required config

**Dependencies:**
- `PyYAML` - YAML parsing

---

## Data Flow

### Flow 1: Casual Conversation

```
User: "@Mitch hey"
    │
    ▼
bot.py:on_message()
    │
    ├─ Check: Is bot mentioned? YES
    ├─ Check: Is game request? NO (just "hey")
    │
    ▼
personality.get_casual_response()
    │
    ├─ Fetch conversation context (last 5 messages)
    ├─ Build system prompt (casual buddy)
    ├─ Build user prompt with context
    │
    ▼
ollama_client.generate()
    │
    ├─ POST to http://localhost:11434/api/generate
    ├─ Wait for response (timeout: 60s)
    │
    ▼
AI Response: "yo what's up?"
    │
    ▼
personality._polish_response(light=True)
    │
    ├─ Remove corporate language
    ├─ Remove excessive punctuation
    ├─ Keep casual tone
    │
    ▼
Discord: "yo what's up?"
```

---

### Flow 2: Game Suggestion Request

```
User: "@Mitch what should we play?"
    │
    ▼
bot.py:on_message()
    │
    ├─ Check: Is bot mentioned? YES
    ├─ Check: Is game request? YES ("what should we play")
    │
    ▼
suggestion_engine.get_suggestion()
    │
    ├─ Count online members: 4 players
    │
    ▼
game_tracker.get_games_for_player_count(4)
    │
    ├─ Query: SELECT * FROM games WHERE min_players <= 4 AND max_players >= 4
    ├─ Result: 8 games found
    │
    ▼
game_tracker.get_recent_plays(days=7)
    │
    ├─ Query: SELECT game_id, played_date FROM play_history WHERE played_date > NOW - 7 days
    ├─ Result: 3 games played in last 48h
    │
    ▼
suggestion_engine._filter_by_cooldown()
    │
    ├─ Remove games played < 48h ago
    ├─ Result: 5 games remaining
    │
    ▼
suggestion_engine._build_suggestion_context()
    │
    ├─ Format: "Available games: Deep Rock Galactic (co-op), Valheim (co-op), ..."
    ├─ Add: "Recently played: Phasmophobia (2 days ago), ..."
    │
    ▼
personality.get_suggestion_response()
    │
    ├─ Build system prompt (gaming buddy, pick 1-2 games)
    ├─ Add game context
    │
    ▼
ollama_client.generate()
    │
    ├─ POST to Ollama
    ├─ Wait for response
    │
    ▼
AI Response: "I'd suggest Deep Rock Galactic - great for 4 people and you haven't played it in a while! Rock and stone!"
    │
    ▼
personality._polish_response(strict=True)
    │
    ├─ Remove corporate language
    ├─ Remove emojis
    ├─ Fix capitalization
    ├─ Trim to max length
    │
    ▼
suggestion_engine._record_suggestion()
    │
    ├─ INSERT INTO suggestions (game_name, player_count, response, suggested_at)
    │
    ▼
Discord: "how about Deep Rock Galactic? great for 4 and you guys haven't touched that in a while"
```

---

## Database Schema

### Tables

#### `games`
Stores the game library with player count requirements.

```sql
CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    min_players INTEGER NOT NULL,
    max_players INTEGER NOT NULL,
    category TEXT NOT NULL,  -- e.g., 'co-op', 'competitive', 'party'
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example Data:**
```
id | name                  | min_players | max_players | category    
---|-----------------------|-------------|-------------|-------------
1  | Deep Rock Galactic    | 1           | 4           | co-op       
2  | Among Us              | 4           | 10          | party       
3  | Valheim               | 1           | 10          | co-op       
```

---

#### `play_history`
Tracks when games were played to implement cooldown system.

```sql
CREATE TABLE play_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    played_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);
```

**Example Data:**
```
id | game_id | played_date          
---|---------|----------------------
1  | 1       | 2026-02-11 20:30:00  
2  | 3       | 2026-02-12 19:15:00  
3  | 1       | 2026-02-13 21:00:00  
```

**Indexes:**
```sql
CREATE INDEX idx_play_history_date ON play_history(played_date);
CREATE INDEX idx_play_history_game ON play_history(game_id);
```

---

#### `suggestions`
Logs AI suggestions for analytics and improvement.

```sql
CREATE TABLE suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_name TEXT NOT NULL,
    player_count INTEGER,
    response TEXT NOT NULL,  -- Full AI response
    suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example Data:**
```
id | game_name           | player_count | response                          | suggested_at         
---|---------------------|--------------|-----------------------------------|----------------------
1  | Deep Rock Galactic  | 4            | "how about Deep Rock? solid..."  | 2026-02-13 20:00:00  
2  | Valheim             | 3            | "maybe Valheim? good for 3"      | 2026-02-13 20:15:00  
```

**Future Use Cases:**
- Track suggestion acceptance rate
- Identify most suggested games
- Analyze AI response quality
- A/B test different prompts

---

### Database Relationships

```
games (1) ──────< (N) play_history
  │
  └─ Foreign key enforced
  └─ Cascading deletes (remove game → remove history)

suggestions
  └─ No foreign key (game_name is text, allows tracking even after game deleted)
```

---

## Configuration System

### Config File Structure

```yaml
discord:          # Discord API settings
ollama:           # AI model configuration  
database:         # SQLite settings
logging:          # Log file settings
suggestions:      # Game suggestion behavior
personality:      # Mitch's character traits
conversation:     # Context tracking (v1.1.0)
rate_limiting:    # Spam prevention (v1.1.0)
features:         # Feature flags
admin:            # Admin user IDs
performance:      # Caching and concurrency
development:      # Debug settings
```

**See [docs/CONFIGURATION.md](CONFIGURATION.md) for complete reference.**

---

### Config Loading Flow

```
1. bot.py starts
2. config_loader.load_config('config/config.yaml')
3. YAML parsed → Python dict
4. validate_config() checks required fields
5. Config dict passed to all modules
6. Each module extracts its own section
```

**Example:**
```python
# bot.py
config = load_config('config/config.yaml')

# suggestion_engine.py
cooldown = config['suggestions']['cooldown_hours']

# personality.py
temperature = config['ollama']['temperature']
```

---

## Error Handling Strategy

Mitch is designed to **never crash** - graceful degradation at every level.

### Component-Level Error Handling

#### Discord Bot (`bot.py`)
- Malformed messages → Ignore and log
- Rate limiting → Send friendly message
- Event handler exceptions → Log error, continue running

#### Suggestion Engine
- Empty game library → Tell user to populate library
- All games on cooldown → Suggest least recently played
- AI failure → Return text fallback
- Database error → Log and return fallback

#### Personality System
- AI timeout → Return None (caller handles fallback)
- Invalid response → Return polished version or None
- Empty context → Use default prompt

#### Ollama Client
- Connection refused → Return None
- Timeout → Return None after 60s
- Invalid JSON → Return None
- Network error → Return None

#### Game Tracker
- Database locked → Retry with exponential backoff
- Constraint violation → Log warning, continue
- Query error → Log error, return empty list

### Fallback Hierarchy

**For Game Suggestions:**
```
1. Try AI suggestion with filtered games
   └─ Fails → 2. Try AI suggestion with all games (ignore cooldown)
      └─ Fails → 3. Return text fallback: "not sure what's good right now"
```

**For Casual Chat:**
```
1. Try AI response with conversation context
   └─ Fails → 2. Try AI response without context
      └─ Fails → 3. Return simple fallback: "hey"
```

---

## Performance Considerations

### Response Times (MediaServer Hardware)

**Typical Performance:**
- Casual chat: 3-10 seconds
- Game suggestions: 5-15 seconds
- Database queries: < 50ms
- Cold start (first request after idle): 10-30 seconds

**Memory Usage:**
- Base bot: ~50MB
- During AI inference: ~600MB spike (~79% of 8GB RAM)
- Returns to baseline after response
- Conversation context: ~2KB per channel

---

### Optimization Techniques

#### 1. **Conversation Context Limiting**
- Only store last N messages per channel (default: 5)
- Prevents unbounded memory growth
- Minimal impact on conversation quality

#### 2. **Database WAL Mode**
- Write-Ahead Logging for better concurrency
- Reduces lock contention
- Faster writes during suggestions

#### 3. **Response Polishing**
- Light polish for casual chat (faster)
- Strict polish only for suggestions (slower but higher quality)

#### 4. **Ollama Timeout Tuning**
- Default 60s allows for cold starts
- Can reduce to 30s if Ollama stays warm
- MediaServer uses 60s to be safe

#### 5. **Rate Limiting (Optional)**
- Prevents spam-induced load
- Default: disabled for friend groups
- Enable for larger servers

---

### Scaling Considerations

**Current Design:**
- Single Discord server
- 5-15 concurrent users
- ~10-50 requests per day
- SQLite is sufficient

**If Scaling to Multiple Servers:**
- Keep SQLite per-server (each server = separate database)
- Or migrate to PostgreSQL for centralized database
- Consider Ollama instance per server for isolation
- Add Redis for cross-server conversation context

---

## Technology Choices Explained

### Why Python?
- Discord.py is mature and well-documented
- Easy async/await for Discord events
- Rich ecosystem (sqlite3, aiohttp, PyYAML)
- Good for rapid prototyping

### Why Ollama?
- **Local inference** - No cloud dependencies, no API costs
- **Privacy** - Gaming chat stays on your server
- **phi3:mini** - Lightweight enough for CPU-only hardware
- **Flexibility** - Easy to swap models (llama2, mistral, etc.)

### Why SQLite?
- **Zero configuration** - No database server needed
- **Perfect for small scale** - 5-15 users, hundreds of games
- **WAL mode** - Good enough concurrency for Discord bot
- **Portable** - Single file database

### Why discord.py?
- **Official Python library** for Discord
- **Async-first** - Non-blocking I/O
- **Well-maintained** - Active community
- **Rich features** - Handles intents, events, permissions

---

## Future Architecture Considerations

**Voice Channel Detection (Planned):**
- Add `VoiceStateUpdate` event handler
- Track who's in voice channels
- Prioritize voice state over online members for player count

**Admin Commands (Planned):**
- Add command parser (prefix-based or slash commands)
- Separate permission checking layer
- Admin-only functions in game_tracker

**Steam Integration (Future):**
- Add SteamAPI client module
- Query user libraries
- Auto-populate game database
- Match Steam games to local database

**Multi-Server Support (Future):**
- Separate database per guild_id
- Or single database with guild_id foreign key
- Shared Ollama instance with request queuing

---

## Diagrams

### Component Dependency Graph

```
bot.py
 ├─ suggestion_engine.py
 │   ├─ game_tracker.py
 │   │   └─ config_loader.py
 │   └─ personality.py
 │       ├─ ollama_client.py
 │       └─ config_loader.py
 └─ personality.py
     └─ (same as above)

config_loader.py (shared by all)
```

**Key Insight:** `config_loader` is the only shared dependency. All other modules are cleanly separated.

---

### Request Flow Sequence

```
[User] ──@mention──> [Discord]
                        │
                        ▼
                    [bot.py]
                        │
                ┌───────┴───────┐
                ▼               ▼
        [is_game_request?]
         YES              NO
          │               │
          ▼               ▼
  [suggestion_engine] [personality]
          │               │
          ▼               │
    [game_tracker]        │
          │               │
          ▼               │
    [personality] ◄───────┘
          │
          ▼
    [ollama_client]
          │
          ▼
      [Ollama]
          │
          ▼
    [AI Response]
          │
          ▼
     [Discord]
```

---

## Summary

Mitch's architecture is:
- **Modular** - Each component has one job
- **Resilient** - Graceful error handling at every level
- **Simple** - No over-engineering, no unnecessary abstraction
- **Extensible** - Easy to add features without breaking existing code

The key design philosophy: **Gaming buddy, not enterprise system.** Keep it simple, keep it reliable, keep it fun.

---

**Next Steps:**
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues
- [Configuration Reference](CONFIGURATION.md) - Every config option explained
- [Database Documentation](DATABASE.md) - Schema and queries
- [Development Guide](DEVELOPMENT.md) - How to contribute

---

**Version History:**
- v1.2.0 (Feb 2026) - Initial architecture documentation
