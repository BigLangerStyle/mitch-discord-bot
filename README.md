# Mitch - Your Gaming Buddy Discord Bot

**Version:** 1.1.0 ✅  
**Status:** Production-Ready with Full Conversational AI

---

## What is Mitch?

Mitch is a Discord bot that acts like your gaming buddy - not a corporate assistant. Built for small gaming groups (5-15 people), Mitch helps you figure out what to play when you're stuck in the "idk, what do you want to play?" loop.

### The Vision

Picture this: You and your friends hop into Discord voice. Someone asks, "what should we play?" Instead of the usual back-and-forth, you just @mention Mitch. He knows who's online, what you've played recently, and suggests something that actually fits your vibe.

No flashy commands. No enterprise features. Just a chill bot that helps you pick a game and get playing.

---

## Quick Start

**Ready to run Mitch?** Check out the [QUICKSTART.md](QUICKSTART.md) guide - get up and running in under 10 minutes.

**Prerequisites:**
- Python 3.9+
- Discord bot token ([Create one here](https://discord.com/developers/applications))
- **Ollama with phi3:mini model** ([Install Ollama](https://ollama.ai))

**TL;DR:**
```bash
# Clone and install
git clone https://github.com/yourusername/mitch-discord-bot.git
cd mitch-discord-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install and setup Ollama
# Visit https://ollama.ai to install for your platform
ollama pull phi3:mini

# Configure
cp config/config.yaml.example config/config.yaml
nano config/config.yaml  # Add your Discord bot token

# Setup game library
python3 scripts/setup_games.py populate

# Run
./run.sh
```

**Try it out:**
```
User: @Mitch hey
Mitch: yo what's up?

User: @Mitch what should we play?
Mitch: how about Deep Rock Galactic? you guys haven't touched that in a while
```

---

## Features (v1.1.0)

### ðŸŽ® Game Suggestions (v1.0.0)
- ✅ **Smart Game Suggestions**: Combines AI reasoning with database knowledge
- ✅ **Player Count Awareness**: Suggests games that fit your group size
- ✅ **Cooldown System**: Avoids suggesting recently played games
- ✅ **Game Library Database**: SQLite database for your game collection
- ✅ **Play History Tracking**: Remembers what you've played recently

### ðŸ'¬ Full Conversational AI (v1.1.0)
- ✅ **Natural Conversations**: Talk to Mitch about anything, not just games
- ✅ **Conversation Context**: Mitch remembers recent messages for natural flow
- ✅ **Contextual Responses**: AI understands what you're talking about
- ✅ **Casual Chat Support**: Greetings, thanks, questions all work naturally
- ✅ **Optional Rate Limiting**: Prevent spam (configurable, off by default)

### ðŸ¤– AI & Personality
- ✅ **AI-Powered Responses**: Natural conversations using local Ollama (phi3:mini)
- ✅ **Casual Personality**: Talks like a gaming buddy, not a corporate assistant
- ✅ **Lightweight**: CPU-only inference, runs on modest hardware
- ✅ **Self-Hosted**: Your data stays on your server
- ✅ **Graceful Fallbacks**: Works even if AI is slow or offline

### ðŸš€ Technical
- ✅ **Mention Detection**: Just @Mitch to interact
- ✅ **Smart Routing**: Automatically detects game requests vs casual chat
- ✅ **Production Ready**: systemd service, logging, error handling
- ✅ **Memory Efficient**: Context tracking uses minimal RAM

**Future Enhancements:**
- Admin commands for game management (!addgame, !played)
- Voice channel detection (priority over online members)
- Reaction-based play tracking
- Steam library integration

---

## Current Status

**v0.1.0 (Repository Setup)** - ✅ Complete
- Directory structure established
- Core documentation written
- Project conventions defined
- Ready for implementation

**v0.2.0 (Working Bot Foundation)** - ✅ Complete
- Task 1: Configuration & Logging Foundation ✅
  - Config loader with YAML support
  - Rotating file logging system
  - Error handling utilities
  - Comprehensive unit tests
- Task 2: Discord Bot Core ✅
  - Discord connection with proper intents
  - Mention detection and response
  - Hardcoded casual responses
  - Graceful error handling and shutdown
- Task 3: Deployment & Documentation ✅
  - SystemD service for production deployment
  - QUICKSTART.md guide for easy setup
  - Testing utilities (scripts/test_components.py)
  - Final documentation polish

**v1.0.0 (MVP - Complete)** - ✅ All Tasks Complete
- Task 1: Ollama Integration ✅
  - Ollama API client for local LLM inference
  - Personality system with casual gaming buddy character
  - AI response generation with polishing
  - Fallback responses when AI unavailable
  - Interactive testing utility (scripts/test_ai.py)
- Task 2: Database & Game Tracking ✅
  - SQLite database with games, play_history, and suggestions tables
  - GameTracker module for database operations
  - Game library population script (scripts/setup_games.py)
  - Database testing utility (scripts/test_database.py)
  - Comprehensive database documentation (docs/DATABASE.md)
- Task 3: Smart Suggestions ✅
  - Suggestion engine combining database + AI
  - Player count detection from online members
  - Cooldown system for play history
  - Context-rich AI prompts
  - Graceful degradation for edge cases
  - Interactive testing utility (scripts/test_suggestions.py)
  - Comprehensive suggestion documentation (docs/SUGGESTIONS.md)

- Task 4: Production Polish & Testing ✅
  - Enhanced test_components.py with comprehensive checks
  - health_check.py for production monitoring
  - Updated systemd service with resource limits and security
  - DEPLOYMENT.md guide for production deployment
  - CHANGELOG.md documenting version history
  - Final documentation polish

**v1.0.1 (Bug Fix)** - ✅ Complete
- Fixed suggestion detection to use flexible keyword matching
- Improved natural language understanding for game requests
- Resolved "what game" not triggering suggestions

**v1.1.0 (Full Conversational AI)** - ✅ Complete
- Added conversation context tracking (last 5 messages per channel)
- Implemented casual_response() function for non-game chat
- Added optional rate limiting to prevent spam
- Enhanced personality system with conversation-aware prompts
- Updated configuration with conversation and rate_limiting sections
- All @mentions now route through AI for natural conversations
- Game suggestion logic preserved and unchanged

**Future Versions** - 📋 Planned
- Admin commands (!addgame, !played)
- Voice channel detection
- Reaction tracking
- Steam library integration

---

## Tech Stack

- **Language**: Python 3.9+
- **Discord**: discord.py 2.x
- **AI**: Ollama (local LLM inference with phi3:mini)
- **HTTP Client**: aiohttp (included with discord.py)
- **Database**: SQLite3 with WAL mode
- **Deployment**: systemd service on Linux

---

## Why This Exists

I built this for my gaming group. We'd spend 20 minutes trying to decide what to play, scrolling through Steam libraries, going "eh, not that one" over and over. I wanted something simple - a bot that knows our group, remembers what we played, and just suggests something good.

No enterprise features. No fancy dashboards. Just a helpful bot that feels like part of the crew.

---

## Architecture

```
mitch-discord-bot/
├── src/
│   ├── bot.py              # Main Discord bot with suggestion detection
│   ├── suggestion_engine.py # Smart game recommendation logic
│   ├── ollama_client.py    # Ollama API wrapper
│   ├── personality.py      # Mitch's character & response polishing
│   ├── game_tracker.py     # Database operations
│   ├── config_loader.py    # YAML configuration
│   └── logger.py           # Logging setup
├── scripts/
│   ├── setup_games.py      # Populate game library
│   ├── test_suggestions.py # Interactive suggestion testing
│   ├── test_database.py    # Database tests
│   ├── test_ai.py          # Interactive AI testing
│   ├── test_components.py  # Comprehensive component tests
│   └── health_check.py     # Production health monitoring
├── config/
│   └── config.yaml.example # Configuration template
├── data/                   # Runtime data (logs, DB)
├── docs/
│   ├── DATABASE.md         # Database documentation
│   ├── SUGGESTIONS.md      # Suggestion algorithm explanation
│   ├── DEPLOYMENT.md       # Production deployment guide
│   └── mitch.service       # SystemD service template
└── requirements.txt        # Python dependencies
```

---

## Usage Examples

**Smart Game Suggestions:**
```
User: @Mitch what should we play?

[4 players online, library has 10 games]
[Filters to 5 games that support 4 players]
[Removes 2 played in last 48 hours]
[AI picks from remaining 3]

Mitch: how about Deep Rock Galactic? you guys haven't touched that in a while
```

**Casual Conversation:**
```
User: @Mitch hey
Mitch: yo what's up?

User: @Mitch how are you
Mitch: doing good, ready to help you guys pick something to play
```

**When All Games Are Recent:**
```
User: @Mitch game suggestion

[All 4-player games played in last 48h]
[Suggests least recently played instead]

Mitch: hmm tough call, all your 4-player games were played recently. how about revisiting Overcooked 2?
```

**Game Library Management:**
```bash
# Populate game library with sample games
$ python3 scripts/setup_games.py populate
Setting up Mitch's game library...
✓ Added Phasmophobia (1-4 players, co-op)
✓ Added Valheim (1-10 players, co-op)
...
✓ Library setup complete! Added 16 games.

# List current games
$ python3 scripts/setup_games.py list
Games in library: 16
- Among Us (4-10 players, party)
- Deep Rock Galactic (1-4 players, co-op)
...

# Clear library (if needed)
$ python3 scripts/setup_games.py clear
Cleared 16 games from library
```

**Interactive Testing:**
```bash
# Test suggestions without Discord
$ python3 scripts/test_suggestions.py

Mitch Suggestion Testing Utility
================================

How many players? 4

Filtered games (5):
- Deep Rock Galactic (co-op, 1-4p)
- Overcooked 2 (party, 1-4p)
- Phasmophobia (co-op, 1-4p)
- Lethal Company (co-op, 1-4p)
- Plate Up! (party, 1-4p)

⏳ Calling AI...
✨ Mitch suggests: "how about Deep Rock Galactic? solid for 4"

⏱️  Response time: 3.2s

Record a game as played? (game name or 'n'):
```

**Database Stats:**
```bash
# View suggestion statistics
$ python3 -c "from src.game_tracker import GameTracker; t = GameTracker(); print(t.get_suggestion_stats())"
{
  'total': 15,
  'accepted': 8,
  'recent': 7,
  'most_suggested': [
    {'name': 'Deep Rock Galactic', 'count': 4},
    {'name': 'Valheim', 'count': 3}
  ]
}
```

---

## Configuration

All settings in `config/config.yaml`:

### Suggestion Settings
```yaml
suggestions:
  recent_plays_window: 7    # Days to consider for play history
  cooldown_hours: 48        # Hours before suggesting same game
  max_suggestions: 3        # Max games to suggest at once
  use_player_count: true    # Filter by player count
```

### AI Settings
```yaml
ollama:
  host: "http://localhost:11434"
  model: "phi3:mini"
  temperature: 0.8          # 0.0-1.0 (higher = more creative)
  max_tokens: 300           # Keep responses concise
  timeout: 60               # Request timeout in seconds
```

### Database Settings
```yaml
database:
  path: "data/mitch.db"
  foreign_keys: true
  journal_mode: "WAL"       # Better concurrency
```

---

## How Suggestions Work

When you ask "what should we play?", Mitch:

1. **Detects suggestion request** - Checks for keywords
2. **Estimates player count** - Counts online members
3. **Filters by player count** - Queries games that support your group size
4. **Applies cooldown** - Removes games played in last 48 hours (configurable)
5. **Builds AI context** - Creates prompt with available games and recent history
6. **Generates suggestion** - AI picks 1-2 games and explains why
7. **Records suggestion** - Saves to database for analytics

**For details:** See [docs/SUGGESTIONS.md](docs/SUGGESTIONS.md)

---

## Development

**Project uses feature branches:**
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature
# Make changes, commit
git push origin feature/your-feature
# Create PR to main
```

**Testing before commit:**
```bash
# Test all components
python3 scripts/test_components.py

# Test suggestions interactively
python3 scripts/test_suggestions.py

# Test AI responses
python3 scripts/test_ai.py

# Test database operations
python3 scripts/test_database.py
```

**For full development guidelines:** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Deployment

**Run as systemd service (recommended):**
```bash
# Copy service file
sudo cp docs/mitch.service /etc/systemd/system/

# Edit paths and user
sudo nano /etc/systemd/system/mitch.service

# Enable and start
sudo systemctl enable mitch
sudo systemctl start mitch

# Check status
sudo systemctl status mitch
sudo journalctl -u mitch -f
```

**Manual run (for testing):**
```bash
./run.sh
# or
python3 src/bot.py
```

---

## Troubleshooting

**"Game library is empty"**
```bash
python3 scripts/setup_games.py populate
```

**Ollama connection failed**
```bash
# Check if Ollama is running
ollama serve

# Verify model is downloaded
ollama pull phi3:mini
```

**Bot not responding to mentions**
- Check Discord bot has "Message Content Intent" enabled in Developer Portal
- Verify bot has "Read Messages" and "Send Messages" permissions
- Check logs: `tail -f data/mitch.log`

**Suggestions seem random**
- Check if play history is being recorded
- Adjust cooldown in config (may be too aggressive)
- Verify game library has games: `python3 scripts/setup_games.py list`

**AI responses too slow**
- Normal on slower CPUs (3-15 seconds is expected)
- Increase timeout in config if needed
- MediaServer: Expect 5-20s for suggestions

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Branch naming conventions
- Testing requirements
- PR process

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

- Built for my gaming group who kept asking "what should we play?"
- Powered by [Ollama](https://ollama.ai) for local AI inference
- Uses [discord.py](https://discordpy.readthedocs.io/) for Discord integration
- Inspired by the universal struggle of indecisive gamers everywhere

---

**Version History:** See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

---

**Questions?** Open an issue or check the [docs/](docs/) directory for detailed documentation.
