# Mitch - Your Gaming Buddy Discord Bot

**Version:** 1.0.0 ✅  
**Status:** Production-Ready with Database Integration

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
Mitch: hmm not sure what the vibe is - competitive or co-op?
```

---

## Features (v1.0.0)

- ✅ **AI-Powered Responses**: Natural conversations using local Ollama (phi3:mini)
- ✅ **Game Library Database**: SQLite database for your game collection
- ✅ **Play History Tracking**: Remembers what you've played recently
- ✅ **Casual Personality**: Talks like a gaming buddy, not a corporate assistant
- ✅ **Mention Detection**: Just @Mitch to get suggestions
- ✅ **Lightweight**: CPU-only inference, runs on modest hardware
- ✅ **Self-Hosted**: Your data stays on your server
- ✅ **Graceful Fallbacks**: Works even if AI is slow or offline

**Coming Soon:**
- Context-aware suggestions using game library
- Voice channel detection
- Admin commands for game management

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
  - Component tests for validation
- Task 3: Deployment & Documentation ✅
  - SystemD service for production deployment
  - QUICKSTART.md guide for easy setup
  - Testing utilities (scripts/test_components.py)
  - Final documentation polish

**v1.0.0 Task 1 (Ollama Integration)** - ✅ Complete
- Ollama API client for local LLM inference
- Personality system with casual gaming buddy character
- AI response generation with polishing
- Fallback responses when AI unavailable
- Interactive testing utility (scripts/test_ai.py)
- Documentation updates

**v1.0.0 Task 2 (Database & Game Tracking)** - ✅ Complete
- SQLite database with games, play_history, and suggestions tables
- GameTracker module for database operations
- Game library population script (scripts/setup_games.py)
- Database testing utility (scripts/test_database.py)
- Comprehensive database documentation (docs/DATABASE.md)
- Foreign key constraints and performance indexes

**Future Enhancements** - 📋 Planned
- Context-aware suggestion engine (using game library + AI)
- Admin commands (!addgame, !played)
- Voice channel detection
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
│   ├── bot.py              # Main Discord bot
│   ├── ollama_client.py    # Ollama API wrapper
│   ├── personality.py      # Mitch's character & response polishing
│   ├── game_tracker.py     # Database operations
│   ├── config_loader.py    # YAML configuration
│   └── logger.py           # Logging setup
├── scripts/
│   ├── setup_games.py      # Populate game library
│   ├── test_database.py    # Database tests
│   ├── test_ai.py          # Interactive AI testing
│   └── test_components.py  # Component tests
├── config/
│   └── config.yaml.example # Configuration template
├── data/                   # Runtime data (logs, DB)
├── docs/
│   ├── DATABASE.md         # Database documentation
│   └── mitch.service       # SystemD service template
└── requirements.txt        # Python dependencies
```

---

## Usage Examples

**Basic Interaction:**
```
User: @Mitch hey
Mitch: yo what's up?

User: @Mitch what should we play?
Mitch: not sure what the vibe is - competitive or chill?

User: @Mitch something co-op for 4 people
Mitch: hmm I don't have your game library set up yet, but for 4 people co-op usually works well
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
Mitch's Game Library (16 games):
CO-OP:
  • Phasmophobia (1-4 players) - horror, investigation, voice-chat
  • Valheim (1-10 players) - survival, building, viking
...

# Show statistics
$ python3 scripts/setup_games.py stats
Mitch Database Statistics:
  Total Games: 16
  Total Plays: 42
  Total Suggestions: 28
```

**Testing AI Responses:**
```bash
$ python3 scripts/test_ai.py

Mitch AI Testing Utility
Connected to Ollama (phi3:mini)

You: what should we play?
[Response time: 2.1s]
Mitch: not sure yet - what kind of games do you have?

You: something fun for 4 players
[Response time: 1.8s]
Mitch: co-op or competitive?
```

---

## Configuration

Mitch uses a single YAML config file. Copy `config/config.yaml.example` to `config/config.yaml` and customize:

**Key Settings:**
```yaml
discord:
  token: "YOUR_BOT_TOKEN"  # From Discord Developer Portal
  
ollama:
  host: "http://localhost:11434"
  model: "phi3:mini"
  temperature: 0.8  # Balance of creativity
  max_tokens: 300   # Keep responses brief
  timeout: 60       # Request timeout

database:
  path: "data/mitch.db"
  foreign_keys: true
  journal_mode: "WAL"
  
logging:
  level: "INFO"
  file: "data/mitch.log"
```

---

## Deployment

**Linux (systemd service):**
```bash
# Copy service file
sudo cp docs/mitch.service /etc/systemd/system/

# Edit service file with your paths
sudo nano /etc/systemd/system/mitch.service

# Enable and start
sudo systemctl enable mitch
sudo systemctl start mitch

# Check status
sudo systemctl status mitch
sudo journalctl -u mitch -f
```

**Manual Run:**
```bash
./run.sh
```

---

## Development

**Running Tests:**
```bash
python3 scripts/test_components.py  # Component tests
python3 scripts/test_database.py    # Database tests
python3 scripts/test_ai.py          # Interactive AI testing
```

**Project Structure:**
- Follow `.agent/project-preferences.md` for coding standards
- Use feature branches for development
- Test on both dev machine and MediaServer before merging

---

## Contributing

Want to contribute? Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick Contribution Guide:**
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/cool-thing`)
3. Follow the coding style in `.agent/project-preferences.md`
4. Test your changes
5. Submit a PR

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Roadmap

**v1.0.0 (Current):** ✅
- Basic AI responses with Ollama
- Casual gaming buddy personality
- Mention detection
- Game library database
- Play history tracking

**v1.1.0 (Next):**
- Context-aware suggestion engine
- Integration of AI + database for smart suggestions
- Voice channel detection

**v1.2.0 (Future):**
- Admin commands
- Enhanced personality
- Reaction-based play tracking

**v2.0.0 (Vision):**
- Steam library integration
- Multi-server support
- Game statistics dashboard

---

## Support

**Issues?** Open an issue on GitHub.

**Questions?** Check the docs:
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
- [DATABASE.md](docs/DATABASE.md) - Database documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
- `.agent/project-preferences.md` - Code standards

---

## Credits

Built with love for small gaming groups by someone tired of "what should we play?" conversations.

**Tech:**
- [discord.py](https://discordpy.readthedocs.io/) - Discord bot framework
- [Ollama](https://ollama.ai) - Local LLM inference
- [phi3:mini](https://ollama.ai/library/phi3) - Lightweight AI model
- [SQLite](https://www.sqlite.org/) - Embedded database

---

**Let's game! 🎮**
