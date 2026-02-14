# Configuration Reference

**Version:** 1.2.0  
**Last Updated:** February 2026

Complete reference for all configuration options in `config/config.yaml`.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Discord Configuration](#discord-configuration)
- [Ollama / AI Configuration](#ollama--ai-configuration)
- [Database Configuration](#database-configuration)
- [Logging Configuration](#logging-configuration)
- [Game Suggestion Settings](#game-suggestion-settings)
- [Personality Configuration](#personality-configuration)
- [Conversation Settings](#conversation-settings-v110)
- [Rate Limiting](#rate-limiting-v110)
- [Feature Flags](#feature-flags)
- [Admin Settings](#admin-settings)
- [Performance Settings](#performance-settings)
- [Development Settings](#development-settings)
- [Configuration Examples](#configuration-examples)

---

## Quick Start

**Initial Setup:**

```bash
# Copy template
cp config/config.yaml.example config/config.yaml

# Edit configuration
nano config/config.yaml
```

**Minimum required changes:**
1. Add your Discord bot token
2. Add your Discord guild (server) ID
3. Verify Ollama settings match your setup

**Test configuration:**
```bash
python3 -c "from src.config_loader import load_config; print('Config valid!')"
```

---

## Discord Configuration

### discord.token

**Type:** String (required)  
**Example:** `"paste_your_discord_token_here"`

**Description:**  
Your Discord bot token from the Discord Developer Portal.

**How to get:**
1. Go to https://discord.com/developers/applications
2. Select your application (or create new)
3. Navigate to "Bot" section
4. Click "Reset Token" or "Copy Token"
5. Paste into config.yaml

**Security:**
- **NEVER commit to git** (already in .gitignore)
- **NEVER share publicly** - anyone with token can control your bot
- If leaked, reset immediately in Developer Portal

**Common Issues:**
- "Improper token" error → Token is invalid, reset and get new one
- Bot won't connect → Double-check token was copied correctly (no extra spaces)

---

### discord.guild_id

**Type:** Integer (required)  
**Example:** `1234567890123456789`

**Description:**  
Your Discord server (guild) ID where bot operates.

**How to get:**
1. Enable Developer Mode in Discord:
   - User Settings → Advanced → Developer Mode (toggle ON)
2. Right-click your server icon in Discord
3. Click "Copy Server ID"
4. Paste into config.yaml (as number, no quotes)

**Why needed:**
- Bot uses guild ID to count online members
- Required for player count detection
- Ensures bot operates in correct server

**Common Issues:**
- Wrong guild_id → Bot might not see correct member count
- Bot can still function in other servers, but player count will be wrong

---

### discord.prefix

**Type:** String (optional)  
**Default:** `"!"`  
**Example:** `"!"` or `null`

**Description:**  
Command prefix for traditional Discord commands (like `!addgame`).

**Current Usage:**
- **v1.1.0:** Not actively used (bot uses @mentions)
- **Future:** Admin commands will use this prefix

**Recommendations:**
- Keep default `"!"` for future admin commands
- Set to `null` or `""` if you never want prefix commands

---

### discord.status

**Type:** String (optional)  
**Default:** `"with your game library"`  
**Example:** `"DRG with the crew"`, `"game suggestions"`

**Description:**  
Bot's "playing" status shown in Discord.

**What it looks like:**
```
Mitch
🟢 Playing with your game library
```

**Customization:**
- Keep it short (< 50 chars)
- Match bot personality (casual, gaming-related)
- Examples: "games with friends", "Rock and Stone!", "what to play?"

**To disable status:**
```yaml
status: null
```

---

## Ollama / AI Configuration

### ollama.host

**Type:** String (required)  
**Default:** `"http://localhost:11434"`

**Description:**  
Ollama API endpoint URL.

**When to change:**

**Running Ollama on different machine:**
```yaml
host: "http://192.168.1.100:11434"
```

**Running Ollama on custom port:**
```yaml
host: "http://localhost:8080"
```

**Important:**
- Must be HTTP (not HTTPS) unless you've configured SSL
- Must include port number
- No trailing slash

**How to verify:**
```bash
curl http://localhost:11434/api/version
```

Expected: `{"version":"0.1.x"}`

---

### ollama.model

**Type:** String (required)  
**Default:** `"phi3:mini"`  
**Recommended:** `"phi3:mini"`

**Description:**  
Which Ollama model to use for AI responses.

**Available Models:**

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **phi3:mini** | 2.3GB | Fast | Good | Gaming chat (recommended) |
| phi3:medium | 7.9GB | Medium | Better | More detailed responses |
| llama2 | 3.8GB | Medium | Good | General conversation |
| mistral | 4.1GB | Medium | Better | Balanced performance |
| codellama | 3.8GB | Medium | Good | Technical discussions |

**How to change:**

```bash
# Pull new model first
ollama pull llama2

# Update config
nano config/config.yaml
# Change: model: "llama2"

# Restart bot
sudo systemctl restart mitch
```

**Performance Impact:**
- Larger models = slower responses, better quality
- phi3:mini is best for CPU-only hardware
- MediaServer (i3-3225) → Use phi3:mini

**Model Not Found Error:**
```bash
# Pull the model
ollama pull phi3:mini

# Verify
ollama list
```

---

### ollama.temperature

**Type:** Float (0.0 - 2.0)  
**Default:** `0.8`  
**Recommended Range:** 0.6 - 1.0

**Description:**  
Controls AI creativity and randomness.

**Temperature Scale:**

| Value | Behavior | Use Case |
|-------|----------|----------|
| 0.0 | Deterministic, same response every time | Testing, consistency |
| 0.3 | Very focused, minimal creativity | Factual responses |
| 0.5 | Balanced, some variety | Structured suggestions |
| **0.8** | **Creative, good variety (default)** | **Casual gaming chat** |
| 1.0 | Very creative, lots of variety | Storytelling, humor |
| 1.5+ | Chaotic, unpredictable | Experimental |

**When to adjust:**

**Responses too repetitive:**
```yaml
temperature: 0.9  # Increase creativity
```

**Responses too random/chaotic:**
```yaml
temperature: 0.6  # Reduce randomness
```

**Want consistent testing:**
```yaml
temperature: 0.0  # Same response every time
```

---

### ollama.max_tokens

**Type:** Integer  
**Default:** `300`  
**Recommended Range:** 200 - 500

**Description:**  
Maximum response length in tokens (~4 characters per token).

**Token Guidelines:**

| Tokens | Characters | Use Case |
|--------|------------|----------|
| 100 | ~400 chars | Very brief (1-2 sentences) |
| 200 | ~800 chars | Short responses |
| **300** | **~1200 chars** | **Good for gaming chat (default)** |
| 500 | ~2000 chars | Detailed explanations |
| 1000+ | ~4000+ chars | Long-form content (slow!) |

**Impact:**
- **Lower:** Faster responses, more concise, might cut off
- **Higher:** Slower responses, more detailed, higher memory usage

**When to adjust:**

**Responses getting cut off:**
```yaml
max_tokens: 400
```

**Want faster responses:**
```yaml
max_tokens: 200
```

**For MediaServer (limited RAM):**
```yaml
max_tokens: 250  # Reduce memory usage
```

---

### ollama.timeout

**Type:** Integer (seconds)  
**Default:** `60`  
**Recommended Range:** 30 - 600

**Description:**  
How long to wait for Ollama response before giving up.

**Timeout Considerations:**

**Fast hardware (modern CPU):**
```yaml
timeout: 30  # AI responds in 5-15 seconds
```

**Modest hardware (like MediaServer i3-3225):**
```yaml
timeout: 60  # AI responds in 10-30 seconds (cold start)
```

**Very slow hardware:**
```yaml
timeout: 120  # Give AI 2 minutes
```

**MediaServer specific:**
- Cold start (first request after idle): 10-30 seconds
- Warm requests: 3-10 seconds
- **Recommendation:** 60 seconds is safe

**What happens on timeout:**
- Ollama request aborted
- Bot returns fallback message
- Error logged
- Bot continues working (doesn't crash)

**Never set below 20s** - even fast hardware needs time for complex requests

---

## Database Configuration

### database.path

**Type:** String (required)  
**Default:** `"data/mitch.db"`

**Description:**  
Path to SQLite database file.

**Path Types:**

**Relative (recommended):**
```yaml
path: "data/mitch.db"  # Relative to project root
```

**Absolute:**
```yaml
path: "/home/user/git/mitch-discord-bot/data/mitch.db"
```

**When to use absolute:**
- Running bot from different directory
- Systemd service with specific WorkingDirectory
- Shared database across multiple instances (not recommended)

**Important:**
- Directory must exist (`data/` must exist)
- User running bot must have write permissions
- Don't put database in `/tmp` (will be deleted on reboot)

---

### database.foreign_keys

**Type:** Boolean  
**Default:** `true`  
**Recommended:** `true` (don't change)

**Description:**  
Enable SQLite foreign key constraints.

**What it does:**
- Enforces relationships between tables
- Deleting a game also deletes its play history (CASCADE)
- Prevents orphaned records

**Should you change this?**
- **No.** Keep it `true` for data integrity.

**If set to `false`:**
- Data integrity not enforced
- Orphaned records possible
- Database might become inconsistent

---

### database.journal_mode

**Type:** String  
**Default:** `"WAL"`  
**Options:** `DELETE`, `TRUNCATE`, `PERSIST`, `MEMORY`, `WAL`, `OFF`  
**Recommended:** `"WAL"` (don't change)

**Description:**  
SQLite journaling mode for concurrent access and crash recovery.

**Journal Modes:**

| Mode | Concurrency | Performance | Use Case |
|------|-------------|-------------|----------|
| **WAL** | Best | Fast writes | **Production (recommended)** |
| DELETE | Good | Slower | Default SQLite |
| TRUNCATE | Good | Medium | Reduced I/O |
| PERSIST | Good | Medium | Persistent journal |
| MEMORY | Poor | Fast | Testing (data loss risk) |
| OFF | Poor | Fastest | No safety (dangerous!) |

**Why WAL is recommended:**
- Better concurrency (readers don't block writers)
- Faster writes during suggestion requests
- Better for production use
- Standard for modern SQLite applications

**When to change:**
- **Don't.** WAL is best for this use case.

**To verify WAL is active:**
```bash
sqlite3 data/mitch.db "PRAGMA journal_mode;"
# Should output: wal
```

---

## Logging Configuration

### logging.level

**Type:** String  
**Default:** `"INFO"`  
**Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Description:**  
Minimum log level to record.

**Log Levels:**

| Level | What You See | When to Use |
|-------|--------------|-------------|
| **DEBUG** | Everything (very verbose) | **Troubleshooting issues** |
| **INFO** | Normal operations | **Production (default)** |
| WARNING | Unusual but not broken | Monitoring |
| ERROR | Something failed | Minimal logging |
| CRITICAL | Critical failures only | Extreme minimal logging |

**Examples:**

**Normal production:**
```yaml
level: "INFO"
```

**Troubleshooting:**
```yaml
level: "DEBUG"
```

**Minimal logging:**
```yaml
level: "WARNING"
```

**What each level shows:**

```
DEBUG:   Import details, function calls, AI prompts, database queries
INFO:    Bot started, message received, suggestion generated
WARNING: Ollama slow, rate limited user, unusual behavior
ERROR:   Ollama timeout, database error, Discord API error
CRITICAL: Can't connect to Discord, database corrupted, fatal crash
```

---

### logging.file

**Type:** String  
**Default:** `"data/mitch.log"`

**Description:**  
Path to log file.

**Recommendations:**
- Keep in `data/` directory
- Use `.log` extension
- Ensure directory exists

**Important:**
- If running as systemd service, logs also go to journald
- Can disable file logging by setting to `null`

---

### logging.format

**Type:** String  
**Default:** `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`

**Description:**  
Python logging format string.

**Default format produces:**
```
2026-02-13 20:30:15,123 - bot - INFO - Received message from user
```

**Custom formats:**

**Simpler:**
```yaml
format: "%(levelname)s: %(message)s"
# Output: INFO: Received message from user
```

**More detailed:**
```yaml
format: "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
# Output: 2026-02-13 20:30:15 [INFO] bot.on_message:45 - Received message
```

**Recommendation:** Keep default unless you have specific needs

---

### logging.max_bytes

**Type:** Integer (bytes)  
**Default:** `10485760` (10MB)

**Description:**  
Maximum log file size before rotation.

**Common Values:**

| Value | Size | Use Case |
|-------|------|----------|
| 1048576 | 1MB | Testing |
| 5242880 | 5MB | Light logging |
| **10485760** | **10MB** | **Normal (default)** |
| 52428800 | 50MB | Heavy logging |
| 0 | Unlimited | No rotation (not recommended) |

**What happens when limit reached:**
- Current log renamed to `mitch.log.1`
- New empty `mitch.log` created
- Old rotated logs eventually deleted (see backup_count)

---

### logging.backup_count

**Type:** Integer  
**Default:** `3`

**Description:**  
Number of rotated log files to keep.

**Example with 3 backups:**
```
data/
  ├── mitch.log         (current, up to 10MB)
  ├── mitch.log.1       (previous, 10MB)
  ├── mitch.log.2       (older, 10MB)
  └── mitch.log.3       (oldest, 10MB)
```

**Total disk space:** `10MB × (backup_count + 1)`

**Recommendations:**
- Small disk: `backup_count: 1` (20MB total)
- Normal: `backup_count: 3` (40MB total)
- Heavy logging: `backup_count: 5` (60MB total)

---

## Game Suggestion Settings

### suggestions.recent_plays_window

**Type:** Integer (days)  
**Default:** `7`

**Description:**  
How many days of play history to consider when building suggestions.

**Not the same as cooldown!**
- `recent_plays_window`: How far back to look for context
- `cooldown_hours`: How long before re-suggesting a game

**Example:**
```yaml
recent_plays_window: 7  # "You played DRG 5 days ago"
```

**When to adjust:**

**Want more historical context:**
```yaml
recent_plays_window: 14
```

**Want less historical context:**
```yaml
recent_plays_window: 3
```

**Impact:**
- Higher = More context for AI, slightly slower queries
- Lower = Less context, faster

**Recommendation:** Keep at 7 days for good context

---

### suggestions.cooldown_hours

**Type:** Integer (hours)  
**Default:** `48`

**Description:**  
Minimum hours before suggesting same game again.

**Tuning Guide:**

| Library Size | Recommended Cooldown | Reasoning |
|--------------|---------------------|-----------|
| < 10 games | 24-36 hours | Prevent staleness |
| 10-20 games | **48 hours (default)** | Good balance |
| 20-30 games | 48-72 hours | More variety possible |
| 30+ games | 72-96 hours | Plenty of options |

**Examples:**

**Small library (10 games):**
```yaml
cooldown_hours: 24  # 1 day
```

**Large library (30 games):**
```yaml
cooldown_hours: 72  # 3 days
```

**Play daily:**
```yaml
cooldown_hours: 24  # Quick rotation
```

**Play weekly:**
```yaml
cooldown_hours: 168  # 1 week, prevent repeats
```

**What happens if all games on cooldown:**
- Bot suggests least recently played game instead
- Cooldown temporarily ignored to provide suggestion

---

### suggestions.max_suggestions

**Type:** Integer  
**Default:** `3`  
**Recommended Range:** 1-5

**Description:**  
Maximum number of games to suggest in one response.

**Behavior by value:**

**1 suggestion:**
```yaml
max_suggestions: 1
```
Response: "how about Deep Rock Galactic?"

**3 suggestions (default):**
```yaml
max_suggestions: 3
```
Response: "how about Deep Rock Galactic? or Valheim or Phasmophobia"

**5 suggestions:**
```yaml
max_suggestions: 5
```
Response: "maybe DRG, Valheim, Phasmophobia, Lethal Company, or Plate Up"

**Recommendations:**
- **1:** Groups that hate choices, want bot to decide
- **3:** Good balance (default)
- **5:** Groups that like options

**Impact:**
- More suggestions = Longer AI responses
- Fewer suggestions = Quicker, more decisive

---

### suggestions.use_player_count

**Type:** Boolean  
**Default:** `true`  
**Recommended:** `true`

**Description:**  
Filter games by player count before suggesting.

**When `true`:**
- Bot counts online members
- Only suggests games that support that player count
- More relevant suggestions

**When `false`:**
- Ignores player count
- Suggests from entire library
- Might suggest 10-player game when only 2 online

**When to disable:**
- Testing with empty server
- Want suggestions regardless of player count
- Manually controlling context

**Recommendation:** Keep `true` for production

---

## Personality Configuration

### personality.name

**Type:** String  
**Default:** `"Mitch"`

**Description:**  
Bot's display name in responses (currently not used in v1.1.0, reserved for future features).

**Future use:**
- Self-reference in responses
- Introduction messages
- Admin command feedback

---

### personality.style

**Type:** String  
**Default:** `"casual"`  
**Options:** `casual`, `formal`, `chaotic`

**Description:**  
Overall response style (currently not actively used, personality is in system prompts).

**Styles:**
- **casual:** Gaming buddy, laid-back (default)
- **formal:** Professional, polite (not recommended for gaming bot)
- **chaotic:** Random, unpredictable (experimental)

**Current implementation:**
- Style is defined in `personality.py` system prompts
- This config value reserved for future customization

---

### personality.use_slang

**Type:** Boolean  
**Default:** `true`

**Description:**  
Allow gaming slang in responses (currently in system prompts, not config-controlled).

**Examples of slang:**
- "ggs" (good games)
- "lol"
- "what's the vibe"
- "solid for 4"

**Future feature:** May add config control for slang level

---

### personality.max_response_length

**Type:** Integer (characters)  
**Default:** `500`

**Description:**  
Hard limit for response length (currently enforced in personality.py).

**Relationship to ollama.max_tokens:**
- `max_tokens`: How many tokens AI generates
- `max_response_length`: Hard cutoff after polishing

**Why both exist:**
- AI might generate more than expected
- Polishing can add characters
- Ensures responses never exceed Discord limits

**Recommendations:**
- Keep at 500 for suggestions
- Can reduce to 300 for very brief responses

---

## Conversation Settings (v1.1.0)

### conversation.context_messages

**Type:** Integer  
**Default:** `5`  
**Recommended Range:** 3-7

**Description:**  
Number of recent messages to include as context for casual chat.

**What it does:**
- Bot fetches last N messages from channel
- Includes them in AI prompt
- Allows AI to understand conversation flow

**Example (context_messages: 5):**
```
User1: anyone playing tonight?
User2: yeah I'm down
User1: @Mitch what should we play?

Bot sees all 3 messages above for context
```

**Impact:**

**More context (7):**
- Better conversation awareness
- AI understands references better
- Slightly higher memory usage
- Slightly slower responses

**Less context (3):**
- Faster responses
- Lower memory usage
- Might miss conversation nuance

**Recommendations:**
- Small server: 7 (more context is nice)
- Busy server: 3 (reduce noise)
- MediaServer: 5 (good balance)

**Memory impact per channel:**
```
~500 bytes × context_messages × active_channels
```
Example: 5 messages × 3 channels = ~7.5KB (negligible)

---

### conversation.casual_max_length

**Type:** Integer (characters)  
**Default:** `300`

**Description:**  
Maximum length for casual chat responses (shorter than suggestions).

**Why different from personality.max_response_length:**
- Casual chat should be snappy
- Suggestions can be more detailed
- Keeps conversation flowing

**Recommendations:**
- **Quick chat:** 200
- **Normal:** 300 (default)
- **Detailed:** 400

**Comparison:**
```yaml
conversation:
  casual_max_length: 300  # "yo what's up?" responses

personality:
  max_response_length: 500  # Game suggestions
```

---

### conversation.casual_light_polish

**Type:** Boolean  
**Default:** `true`

**Description:**  
Use light response polishing for casual chat (vs strict for suggestions).

**Polishing modes:**

**Light polish (casual chat):**
- Removes corporate language
- Removes excessive punctuation
- Keeps natural tone
- Fast

**Strict polish (suggestions):**
- All of light polish, plus:
- Removes emojis
- Fixes capitalization
- Trims to exact length
- Slower but cleaner

**When to disable (set to `false`):**
- Want raw AI responses for casual chat
- Testing prompt engineering
- Debugging personality issues

**Recommendation:** Keep `true` for best results

---

## Rate Limiting (v1.1.0)

### rate_limiting.enabled

**Type:** Boolean  
**Default:** `false`  
**Recommended:** `false` for friend groups, `true` for public servers

**Description:**  
Enable spam prevention for @mentions.

**When to enable:**
- Public server with strangers
- Friends are spamming for fun
- Want to reduce Ollama load
- Concerns about abuse

**When to disable (default):**
- Small friend group (5-15 people)
- Trust your users
- Want maximum responsiveness
- No spam concerns

**Behavior when enabled:**
- Tracks last @mention time per user
- If user @mentions too quickly → Sends cooldown message
- After cooldown expires → Normal responses resume

---

### rate_limiting.cooldown_seconds

**Type:** Integer (seconds)  
**Default:** `5`  
**Recommended Range:** 3-10

**Description:**  
Minimum seconds between @mentions per user.

**Tuning guide:**

| Cooldown | Use Case | User Experience |
|----------|----------|-----------------|
| 3 | Light protection | Barely noticeable |
| **5** | **Balanced (default)** | **Prevents rapid spam** |
| 10 | Strict | Might frustrate users |
| 30 | Very strict | Only for abuse cases |

**What happens:**
```
User: @Mitch hey
Bot: yo what's up?

[2 seconds later]
User: @Mitch what should we play?
Bot: whoa slow down a sec!  [rate limited]

[5 seconds total from first message]
User: @Mitch what should we play?
Bot: how about DRG?  [allowed]
```

**Recommendation:** Start with 5, adjust if needed

---

### rate_limiting.message

**Type:** String  
**Default:** `"whoa slow down a sec!"`

**Description:**  
Message sent when user is rate limited.

**Customization examples:**
```yaml
message: "give me a sec to think!"
message: "one at a time lol"
message: "chill, I need a moment"
message: "easy there, I'm working on it"
```

**Keep it:**
- Short (< 50 chars)
- Friendly, not harsh
- Matches Mitch's personality (casual)

---

## Feature Flags

### features.play_tracking

**Type:** Boolean  
**Default:** `true`

**Description:**  
Enable play history tracking.

**When `true`:**
- Suggestions record play history
- Cooldown system works
- Analytics available

**When `false`:**
- No play history recorded
- Cooldown doesn't work
- All suggestions fresh every time

**Recommendation:** Keep `true` unless debugging

---

### features.admin_commands

**Type:** Boolean  
**Default:** `false`

**Description:**  
Enable admin commands (!addgame, !played, etc.).

**Status:** Not yet implemented (future feature)

**When implemented:**
```yaml
features:
  admin_commands: true
```

Enables:
- `!addgame <name> <min> <max> <category>`
- `!played <game>`
- `!games list`
- `!stats`

---

### features.voice_detection

**Type:** Boolean  
**Default:** `false`

**Description:**  
Prioritize voice channel members over online members.

**Status:** Not yet implemented (future feature)

**When implemented:**
- Bot monitors voice channels
- Uses voice state for player count
- More accurate than online member count

---

### features.reaction_tracking

**Type:** Boolean  
**Default:** `false`

**Description:**  
Auto-record plays when users react to suggestions.

**Status:** Not yet implemented (future feature)

**When implemented:**
- User reacts ✅ to suggestion
- Bot automatically records that game as played

---

### features.steam_integration

**Type:** Boolean  
**Default:** `false`

**Description:**  
Fetch games from Steam libraries.

**Status:** Not yet implemented (future feature)

**When implemented:**
- Connect Steam accounts
- Auto-populate game library from Steam
- Show which games group owns

---

## Admin Settings

### admin.user_ids

**Type:** List of Integers  
**Default:** `[1234567890123456789]`

**Description:**  
Discord user IDs with admin privileges.

**How to get your user ID:**
1. Enable Developer Mode in Discord
2. Right-click your name
3. Click "Copy User ID"

**Example:**
```yaml
admin:
  user_ids:
    - 123456789012345678  # Your ID
    - 987654321098765432  # Friend's ID
```

**Currently unused (v1.1.0)** - Reserved for future admin commands

---

### admin.role_ids

**Type:** List of Integers  
**Default:** `[9876543210987654321]`

**Description:**  
Discord role IDs with admin privileges.

**How to get role ID:**
1. Server Settings → Roles
2. Right-click role
3. Copy ID

**Example:**
```yaml
admin:
  role_ids:
    - 111111111111111111  # Admin role
    - 222222222222222222  # Moderator role
```

**Currently unused (v1.1.0)** - Reserved for future admin commands

---

## Performance Settings

### performance.game_cache_size

**Type:** Integer  
**Default:** `1000`

**Description:**  
Maximum number of games to cache in memory.

**Currently unused (v1.1.0)** - Reserved for future caching implementation

**When implemented:**
- Frequently accessed games cached in RAM
- Reduces database queries
- Faster suggestions

---

### performance.response_cache_ttl

**Type:** Integer (seconds)  
**Default:** `300` (5 minutes)

**Description:**  
How long to cache AI responses.

**Currently unused (v1.1.0)** - Reserved for future caching

**When implemented:**
- Identical requests return cached response
- Reduces Ollama load
- Faster responses for common queries

---

### performance.max_concurrent_ai_requests

**Type:** Integer  
**Default:** `2`

**Description:**  
Maximum simultaneous Ollama requests.

**Currently unused (v1.1.0)** - Single-threaded execution

**Why limit:**
- Ollama is CPU-intensive
- Multiple requests spike RAM usage
- Can overwhelm modest hardware

**Recommendations:**
- Fast hardware: 3-5
- MediaServer: 2 (default)
- Very slow hardware: 1

---

## Development Settings

### development.debug

**Type:** Boolean  
**Default:** `false`

**Description:**  
Enable debug mode with verbose logging.

**When `true`:**
- Sets logging level to DEBUG automatically
- Shows detailed error messages to users
- Logs AI prompts and responses
- Logs database queries

**When to enable:**
- Troubleshooting issues
- Testing new features
- Understanding bot behavior

**Production:** Always `false`

---

### development.auto_reload

**Type:** Boolean  
**Default:** `false`

**Description:**  
Auto-reload bot when code changes detected.

**Currently unused (v1.1.0)** - Future feature

**When implemented:**
- Watches src/ directory
- Restarts bot on file changes
- Useful for development

**Never enable in production!**

---

### development.test_mode

**Type:** Boolean  
**Default:** `false`

**Description:**  
Use test data instead of real database.

**Currently unused (v1.1.0)** - Future feature

**When implemented:**
- Uses test database (data/test.db)
- Doesn't affect production data
- Safe for experimentation

---

## Configuration Examples

### Example 1: Small Friend Group (Default)

```yaml
discord:
  token: "DISCORD_TOKEN"
  guild_id: 1234567890

ollama:
  host: "http://localhost:11434"
  model: "phi3:mini"
  temperature: 0.8
  max_tokens: 300
  timeout: 60

suggestions:
  cooldown_hours: 48
  max_suggestions: 3

conversation:
  context_messages: 5
  casual_max_length: 300

rate_limiting:
  enabled: false  # Trust your friends
```

---

### Example 2: Public Server

```yaml
discord:
  token: "DISCORD_TOKEN"
  guild_id: 1234567890

ollama:
  host: "http://localhost:11434"
  model: "phi3:mini"
  temperature: 0.7  # Slightly more focused
  max_tokens: 300
  timeout: 60

suggestions:
  cooldown_hours: 72  # More games, longer cooldown
  max_suggestions: 2  # Be more decisive

conversation:
  context_messages: 3  # Less context (busier server)
  casual_max_length: 200  # Shorter responses

rate_limiting:
  enabled: true  # Prevent spam
  cooldown_seconds: 10  # Stricter
```

---

### Example 3: Slow Hardware

```yaml
ollama:
  host: "http://localhost:11434"
  model: "phi3:mini"  # Smallest model
  temperature: 0.8
  max_tokens: 250  # Reduce memory usage
  timeout: 120  # Allow more time

conversation:
  context_messages: 3  # Less context
  casual_max_length: 250

logging:
  level: "WARNING"  # Reduce logging overhead
```

---

### Example 4: Fast Hardware

```yaml
ollama:
  host: "http://localhost:11434"
  model: "mistral"  # Larger, better model
  temperature: 0.8
  max_tokens: 500  # More detailed responses
  timeout: 30  # Can afford shorter timeout

conversation:
  context_messages: 7  # More context
  casual_max_length: 400
```

---

### Example 5: Testing/Development

```yaml
logging:
  level: "DEBUG"  # Verbose logging

development:
  debug: true  # Show all details

ollama:
  temperature: 0.0  # Deterministic responses
  timeout: 30

rate_limiting:
  enabled: false  # No rate limits during testing
```

---

## Validation

**After changing config, verify it's valid:**

```bash
# Test config loads
python3 -c "from src.config_loader import load_config; config = load_config('config/config.yaml'); print('✓ Config valid!')"

# Test all components
python3 scripts/test_components.py
```

**Common config errors:**

```yaml
# Wrong: token without quotes
token: DISCORD_TOKEN_GOES_HERE

# Right: token with quotes
token: "DISCORD_TOKEN_GOES_HERE"

# Wrong: guild_id with quotes
guild_id: "1234567890"

# Right: guild_id as number
guild_id: 1234567890

# Wrong: boolean as string
enabled: "true"

# Right: boolean without quotes
enabled: true
```

---

## Quick Reference Table

| Setting | Type | Default | Impact If Changed |
|---------|------|---------|-------------------|
| ollama.timeout | int | 60 | Response wait time |
| ollama.temperature | float | 0.8 | AI creativity |
| ollama.max_tokens | int | 300 | Response length |
| suggestions.cooldown_hours | int | 48 | Re-suggestion delay |
| conversation.context_messages | int | 5 | Conversation awareness |
| rate_limiting.enabled | bool | false | Spam prevention |
| logging.level | string | INFO | Log verbosity |

---

**Related Documentation:**
- [Architecture Overview](ARCHITECTURE.md) - How config is used
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Config-related issues
- [Deployment Guide](DEPLOYMENT.md) - Production config recommendations
