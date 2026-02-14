# Development Guide

**Version:** 1.2.0  
**Last Updated:** February 2026

This guide covers everything you need to know to contribute to or modify the Mitch Discord Bot.

---

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Debugging](#debugging)
- [Adding New Features](#adding-new-features)
- [Common Development Tasks](#common-development-tasks)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting Development Issues](#troubleshooting-development-issues)

---

## Development Environment Setup

### Prerequisites

**Required:**
- Python 3.9 or higher
- Git
- Discord bot token (for testing)
- Ollama with phi3:mini model

**Recommended:**
- IDE with Python support (VSCode, PyCharm, Cursor)
- SQLite browser for database inspection
- Discord server for testing (separate from production)

---

### Initial Setup

**1. Clone and Create Virtual Environment**

```bash
# Clone repository
git clone https://github.com/yourusername/mitch-discord-bot.git
cd mitch-discord-bot

# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

**2. Install Dependencies**

```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
python3 -c "import discord; import yaml; print('✓ Dependencies installed')"
```

**3. Install and Setup Ollama**

```bash
# Install Ollama (visit https://ollama.ai for your platform)

# Pull phi3:mini model
ollama pull phi3:mini

# Verify
ollama list
```

**4. Configure for Development**

```bash
# Copy config template
cp config/config.yaml.example config/config.yaml

# Edit config
nano config/config.yaml
```

**Minimum config for development:**
```yaml
discord:
  token: "YOUR_TEST_BOT_TOKEN"  # Use test bot, not production
  guild_id: 1234567890  # Your test server ID

ollama:
  host: "http://localhost:11434"
  model: "phi3:mini"
  timeout: 60

logging:
  level: "DEBUG"  # Verbose for development

development:
  debug: true  # Show detailed errors
```

**5. Setup Test Database**

```bash
# Populate game library
python3 scripts/setup_games.py populate

# Verify
python3 scripts/setup_games.py list
```

**6. Test Everything**

```bash
# Run component tests
python3 scripts/test_components.py

# Expected output:
# ✓ Config loaded successfully
# ✓ Database connection working
# ✓ Ollama connection working
# ✓ All imports successful
```

---

## Project Structure

```
mitch-discord-bot/
├── .agent/                     # Claude workflow & preferences
│   ├── project-preferences.md
│   └── claude_workflow.md
│
├── config/
│   ├── config.yaml.example     # Configuration template
│   └── config.yaml            # Your config (not in git)
│
├── data/                       # Runtime data (created on first run)
│   ├── mitch.db               # SQLite database
│   └── mitch.log              # Log file
│
├── docs/                       # Technical documentation
│   ├── ARCHITECTURE.md        # Component overview
│   ├── CONFIGURATION.md       # Config reference
│   ├── TROUBLESHOOTING.md     # Common issues
│   ├── DATABASE.md            # Database schema
│   ├── DEPLOYMENT.md          # Production guide
│   └── mitch.service          # SystemD service file
│
├── src/                        # Source code
│   ├── bot.py                 # Main Discord bot
│   ├── suggestion_engine.py   # Game recommendation logic
│   ├── personality.py         # AI prompts & response polishing
│   ├── ollama_client.py       # Ollama API wrapper
│   ├── game_tracker.py        # Database operations
│   ├── config_loader.py       # YAML config loader
│   └── logger.py              # Logging setup
│
├── scripts/                    # Utility scripts
│   ├── setup_games.py         # Populate/manage game library
│   ├── test_components.py     # Component health checks
│   ├── test_suggestions.py    # Interactive suggestion testing
│   ├── test_ai.py             # Interactive AI testing
│   └── test_database.py       # Database tests
│
├── tests/                      # Unit tests (future)
│
├── .gitignore
├── LICENSE
├── README.md
├── QUICKSTART.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── requirements.txt
└── run.sh                      # Quick start script
```

---

### Key Files Explained

**src/bot.py**
- Entry point for the bot
- Discord event handling (on_ready, on_message)
- @mention detection and routing
- Conversation context tracking

**src/suggestion_engine.py**
- Player count detection
- Game filtering (player count, cooldown)
- AI context building for suggestions
- Suggestion recording

**src/personality.py**
- System prompt construction
- Response polishing (light vs strict)
- Mitch's personality definition
- Casual chat vs suggestion routing

**src/ollama_client.py**
- HTTP communication with Ollama
- Timeout handling
- Error recovery

**src/game_tracker.py**
- All database operations
- Game CRUD operations
- Play history tracking
- Suggestion analytics

**src/config_loader.py**
- YAML parsing
- Configuration validation
- Default value handling

---

## Development Workflow

### Git Workflow

**Branch Structure:**
```
main
 ├── feature/voice-detection
 ├── feature/admin-commands
 └── fix/ollama-timeout
```

**Creating a Feature Branch:**

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add src/bot.py
git commit -m "Add voice channel detection

- Monitor voice state changes
- Update player count based on voice
- Add fallback to online members"

# Push to remote
git push origin feature/your-feature-name
```

**Branch Naming Conventions:**
- `feature/descriptive-name` - New features
- `fix/descriptive-name` - Bug fixes
- `docs/descriptive-name` - Documentation updates

---

### Testing Before Commit

**Always run these before committing:**

```bash
# 1. Component health check
python3 scripts/test_components.py

# 2. Test your specific change
# Example: If you modified suggestion_engine.py
python3 scripts/test_suggestions.py

# 3. Run bot locally and test in Discord
./run.sh
# Or manually:
python3 src/bot.py
```

---

### Commit Message Format

**Good commit messages:**
```
Add voice channel detection

- Monitor VoiceStateUpdate events
- Track users in voice channels
- Prioritize voice count over online members
- Add fallback if no voice activity
```

**Bad commit messages:**
```
fix stuff
updated code
changes
```

**Format:**
```
<Short summary (50 chars or less)>

<Blank line>

<Detailed explanation:>
- What changed
- Why it changed
- Any side effects or considerations
```

---

## Code Style Guidelines

### Python Style

**Follow PEP 8 with these specifics:**

**Imports:**
```python
# Standard library first
import asyncio
import logging
from datetime import datetime

# Third-party libraries
import discord
import yaml

# Local modules
from src.config_loader import load_config
from src.game_tracker import GameTracker
```

**Function Naming:**
```python
# Good: Snake case, descriptive
def get_available_games(player_count: int) -> list:
    pass

def should_respond_to_message(message: discord.Message) -> bool:
    pass

# Bad: Camel case, vague
def GetGames(count):
    pass

def check(msg):
    pass
```

**Variable Naming:**
```python
# Good: Descriptive, lowercase with underscores
player_count = 4
available_games = []
cooldown_hours = 48

# Bad: Single letters, abbreviations
pc = 4
avail = []
cd = 48
```

---

### Comments

**When to comment:**
- Complex logic that isn't immediately obvious
- Workarounds for Discord.py or Ollama quirks
- Performance considerations
- Non-obvious design decisions

**Example:**
```python
# Good: Explains WHY, not WHAT
# We use flexible keyword matching instead of exact phrases because users
# phrase requests in many ways ("what should we play", "game suggestions", etc.)
if any(keyword in content.lower() for keyword in game_keywords):
    return True

# Bad: States the obvious
# Check if keyword is in content
if any(keyword in content.lower() for keyword in game_keywords):
    return True
```

**Function Docstrings:**
```python
def filter_games_by_cooldown(games: list, cooldown_hours: int) -> list:
    """
    Remove games played within the cooldown period.
    
    Args:
        games: List of game dictionaries from database
        cooldown_hours: Minimum hours before re-suggesting
        
    Returns:
        List of games not on cooldown (or all games if none available)
        
    Note:
        If all games are on cooldown, returns least recently played instead
        to ensure we always have suggestions.
    """
    # Implementation
```

---

### Error Handling

**Always use try/except for:**
- Database operations
- HTTP requests (Ollama, Discord)
- File I/O
- JSON parsing

**Example:**
```python
# Good: Specific exception, logged error, graceful fallback
try:
    response = await ollama_client.generate(prompt, config)
except asyncio.TimeoutError:
    logger.warning(f"Ollama timeout after {timeout}s")
    return None
except aiohttp.ClientError as e:
    logger.error(f"Ollama connection error: {e}")
    return None

# Bad: Bare except, no logging
try:
    response = await ollama_client.generate(prompt, config)
except:
    return None
```

---

### Async/Await

**Discord.py is async - use async/await properly:**

```python
# Good: Async function with await
async def on_message(self, message: discord.Message):
    if message.author.bot:
        return
    
    async with message.channel.typing():
        response = await self.get_response(message.content)
        await message.channel.send(response)

# Bad: Mixing sync and async
def on_message(self, message):  # Should be async
    response = self.get_response(message.content)  # Should await
    message.channel.send(response)  # Should await
```

---

## Testing

### Component Tests

**Location:** `scripts/test_components.py`

**What it tests:**
- Config loading
- Database connectivity
- Ollama connectivity
- Import integrity

**Run it:**
```bash
python3 scripts/test_components.py
```

**Add tests when you:**
- Add new module dependencies
- Add new config sections
- Add new database tables

---

### Interactive Testing Scripts

**Suggestion Testing:**
```bash
python3 scripts/test_suggestions.py

# Test with different player counts
# Record plays manually
# See AI responses without Discord
```

**AI Testing:**
```bash
python3 scripts/test_ai.py

# Test prompts interactively
# See raw AI output
# Debug personality issues
```

**Database Testing:**
```bash
python3 scripts/test_database.py

# Test CRUD operations
# Verify schema
# Check constraints
```

---

### Manual Testing in Discord

**Create a test server:**
1. Create new Discord server (separate from production)
2. Invite your bot
3. Configure bot with test server guild_id

**Test scenarios:**
- @mention with casual chat
- @mention with game requests
- Various player counts (join/leave voice)
- Edge cases (empty library, all games on cooldown)
- Rate limiting (if enabled)

**Watch logs during testing:**
```bash
# If running manually
tail -f data/mitch.log

# If running as service
sudo journalctl -u mitch -f
```

---

## Debugging

### Debug Mode

**Enable in config:**
```yaml
logging:
  level: "DEBUG"

development:
  debug: true
```

**Restart bot, watch logs:**
```bash
python3 src/bot.py
```

**DEBUG logs show:**
- All function calls
- AI prompts sent to Ollama
- Database queries
- Response polishing steps

---

### Common Debugging Techniques

**1. Print Debugging**
```python
# Add temporary logging
logger.debug(f"Player count: {player_count}")
logger.debug(f"Filtered games: {len(filtered_games)}")
logger.debug(f"AI prompt: {prompt[:100]}...")
```

**2. Interactive Python**
```bash
# Test components in Python REPL
python3

>>> from src.game_tracker import GameTracker
>>> tracker = GameTracker()
>>> games = tracker.get_games_for_player_count(4)
>>> print(games)
```

**3. Database Inspection**
```bash
# Open database in SQLite
sqlite3 data/mitch.db

# Run queries
sqlite> SELECT * FROM games WHERE max_players >= 4;
sqlite> SELECT COUNT(*) FROM play_history;
sqlite> .schema games
```

**4. Ollama Direct Testing**
```bash
# Test Ollama outside bot
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"phi3:mini","prompt":"test","stream":false}' | jq
```

---

### Debug Logging Best Practices

```python
# Good: Useful context, not too verbose
logger.debug(f"Filtering {len(games)} games for {player_count} players")
logger.debug(f"After cooldown filter: {len(filtered)} games remain")

# Bad: Too much detail, clutters logs
for game in games:
    logger.debug(f"Checking game: {game}")
    logger.debug(f"Min players: {game['min_players']}")
    logger.debug(f"Max players: {game['max_players']}")
```

---

## Adding New Features

### Example: Adding a New Database Table

**1. Plan the schema**
```sql
CREATE TABLE game_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    times_suggested INTEGER DEFAULT 0,
    times_played INTEGER DEFAULT 0,
    last_played TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);
```

**2. Add to game_tracker.py**
```python
def create_tables(self):
    # ... existing tables ...
    
    # Add new table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            times_suggested INTEGER DEFAULT 0,
            times_played INTEGER DEFAULT 0,
            last_played TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        )
    """)
```

**3. Add methods to interact with table**
```python
def get_game_stats(self, game_id: int) -> dict:
    """Get statistics for a specific game."""
    with self._connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM game_stats WHERE game_id = ?",
            (game_id,)
        )
        return cursor.fetchone()

def update_game_stats(self, game_id: int, suggested: bool = False, played: bool = False):
    """Update game statistics."""
    with self._connect() as conn:
        cursor = conn.cursor()
        if suggested:
            cursor.execute(
                "UPDATE game_stats SET times_suggested = times_suggested + 1 WHERE game_id = ?",
                (game_id,)
            )
        if played:
            cursor.execute(
                "UPDATE game_stats SET times_played = times_played + 1, last_played = ? WHERE game_id = ?",
                (datetime.now(), game_id)
            )
        conn.commit()
```

**4. Update DATABASE.md documentation**

**5. Test thoroughly**
```bash
# Create test script
python3 -c "
from src.game_tracker import GameTracker
t = GameTracker()
# Test stats retrieval
stats = t.get_game_stats(1)
print(stats)
# Test stats update
t.update_game_stats(1, suggested=True)
"
```

---

### Example: Adding Admin Commands

**1. Add command parser to bot.py**
```python
def is_admin_command(self, message: discord.Message) -> bool:
    """Check if message is an admin command."""
    content = message.content.strip()
    prefix = self.config['discord'].get('prefix', '!')
    
    return content.startswith(prefix) and \
           message.author.id in self.config['admin']['user_ids']

async def handle_admin_command(self, message: discord.Message):
    """Process admin commands."""
    content = message.content.strip()
    prefix = self.config['discord']['prefix']
    
    # Remove prefix
    command = content[len(prefix):].split()
    
    if command[0] == 'addgame':
        await self.cmd_addgame(message, command[1:])
    elif command[0] == 'played':
        await self.cmd_played(message, command[1:])
    # ... more commands
```

**2. Implement command handlers**
```python
async def cmd_addgame(self, message: discord.Message, args: list):
    """Add game to library.
    
    Usage: !addgame "Game Name" min max category
    Example: !addgame "Deep Rock Galactic" 1 4 co-op
    """
    try:
        name = args[0]
        min_p = int(args[1])
        max_p = int(args[2])
        category = args[3]
        
        self.game_tracker.add_game(name, min_p, max_p, category)
        await message.channel.send(f"Added {name} to library!")
        
    except Exception as e:
        logger.error(f"Error in !addgame: {e}")
        await message.channel.send("Usage: !addgame \"name\" min max category")
```

**3. Update config.yaml.example**
```yaml
features:
  admin_commands: true  # Enable admin commands
```

**4. Document in README.md**

---

## Common Development Tasks

### Adding a New Game to Test Library

```bash
# Interactive
python3 scripts/setup_games.py

# Programmatic
python3 -c "
from src.game_tracker import GameTracker
t = GameTracker()
t.add_game('Among Us', 4, 10, 'party')
print('Added Among Us')
"
```

---

### Clearing Play History

```bash
# Clear all history
sqlite3 data/mitch.db "DELETE FROM play_history;"

# Clear for specific game
sqlite3 data/mitch.db "DELETE FROM play_history WHERE game_id = 1;"
```

---

### Testing Different Personality Prompts

**Edit src/personality.py:**
```python
def _build_system_prompt(self, context_type: str) -> str:
    if context_type == "suggestion":
        return """You're Mitch, a casual gaming buddy...
        
        [Modify this to test different personalities]
        """
```

**Test with:**
```bash
python3 scripts/test_ai.py
# Try various prompts
```

---

### Changing AI Model

```bash
# Pull new model
ollama pull llama2

# Update config
nano config/config.yaml
# Change: model: "llama2"

# Test
python3 scripts/test_ai.py
```

---

## Performance Optimization

### Database Query Optimization

**Use indexes for frequently queried columns:**
```sql
CREATE INDEX idx_play_history_date ON play_history(played_date);
CREATE INDEX idx_games_player_count ON games(min_players, max_players);
```

**Avoid N+1 queries:**
```python
# Bad: Query in loop
for game in games:
    plays = tracker.get_plays_for_game(game['id'])  # N queries

# Good: Single query with JOIN
plays = tracker.get_all_recent_plays()  # 1 query
```

---

### Reducing Ollama Response Time

**1. Keep responses concise:**
```yaml
ollama:
  max_tokens: 250  # Down from 300
```

**2. Keep model warm:**
- First request after idle is slow (cold start)
- Subsequent requests are faster
- Consider ping script to keep warm

**3. Reduce context:**
```yaml
conversation:
  context_messages: 3  # Down from 5
```

---

### Memory Optimization

**Monitor memory usage:**
```bash
# Watch bot memory
watch -n 1 'ps aux | grep python | grep mitch'
```

**Reduce memory spikes:**
```yaml
performance:
  max_concurrent_ai_requests: 1  # Down from 2
```

---

## Troubleshooting Development Issues

### "Module not found" Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify imports work
python3 -c "import discord; import yaml; print('OK')"
```

---

### Database Locked Errors

```bash
# Check for multiple bot instances
ps aux | grep python | grep mitch

# Kill old instances
pkill -f "python.*bot.py"

# Ensure WAL mode is enabled
sqlite3 data/mitch.db "PRAGMA journal_mode=WAL;"
```

---

### Bot Not Responding in Test Server

**Check:**
1. Bot token is correct
2. Bot is online in Discord
3. Message Content Intent is enabled
4. Guild ID matches your test server
5. Bot has permissions (Read/Send Messages)

**Debug:**
```bash
# Run with DEBUG logging
python3 src/bot.py
# Watch for "Received message" logs
```

---

### Ollama Connection Refused

```bash
# Start Ollama
ollama serve

# Or if using snap
sudo snap start ollama

# Verify
curl http://localhost:11434/api/version
```

---

## Next Steps

**After reading this guide:**

1. **Set up your dev environment** - Follow setup instructions
2. **Read the code** - Start with bot.py, follow imports
3. **Run tests** - Make sure everything works
4. **Make a small change** - Add a log message, test it
5. **Read other docs:**
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Understand components
   - [CONFIGURATION.md](CONFIGURATION.md) - Config options
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
   - [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

---

**Happy coding! 🎮**

For questions or issues, check the troubleshooting guide or open an issue on GitHub.
