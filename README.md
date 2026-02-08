# Mitch - Your Gaming Buddy Discord Bot

**Version:** 0.2.0 ✅  
**Status:** Production-Ready Discord Bot - Fully Deployed

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

**TL;DR:**
```bash
# Clone and install
git clone https://github.com/yourusername/mitch-discord-bot.git
cd mitch-discord-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp config/config.yaml.example config/config.yaml
nano config/config.yaml  # Add your Discord bot token

# Run
./run.sh
```

**Try it out:**
```
User: @Mitch hey
Mitch: yo what's up?

User: @Mitch what should we play?
Mitch: hmm not sure yet, still setting up my game library
```

*(Note: Game suggestions coming in v0.3.0 - currently using hardcoded responses)*

---

## Features (Planned for v1.0.0)

- **Smart Game Suggestions**: Mitch knows your library and picks games based on who's online
- **Play History Tracking**: Remembers what you played recently to avoid repetition
- **Casual Personality**: Talks like a gaming buddy, not a robot
- **Lightweight**: Runs on a Raspberry Pi or old laptop
- **AI-Powered**: Uses local Ollama (phi3:mini) for natural responses
- **SQLite Database**: Simple, no external database server needed

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

**v0.3.0 (AI Integration)** - 🎯 Next Up
- Ollama integration with phi3:mini model
- Natural language response generation
- Context-aware conversations
- Personality refinement

**v1.0.0 (Full Release)** - 🚀 Goal
- Complete feature set
- Game library and tracking
- Smart suggestions based on players
- Production-ready and stable

---

## Tech Stack

- **Language**: Python 3.9+
- **Discord**: discord.py 2.x
- **AI**: Ollama (local LLM inference)
- **Database**: SQLite3
- **Deployment**: systemd service on Linux

---

## Why This Exists

Most Discord bots are either:
- Over-engineered with features you'll never use
- Too formal and corporate-feeling
- Require cloud hosting and monthly fees
- Built for massive servers, not small friend groups

Mitch is different:
- **Small scale**: 5-15 people, not thousands
- **Self-hosted**: Run it on your own hardware
- **Personality**: Feels like a friend, not a tool
- **Simple**: Does one thing well

---

## Project Philosophy

1. **Simplicity over features**: Better to do a few things well
2. **Personality over formality**: Gaming buddies, not corporate assistants
3. **Self-hosted over cloud**: Your data, your hardware
4. **Customizable over rigid**: Easy to tweak for your group

---

## Quick Links

- **[Setup Guide (QUICKSTART.md)](QUICKSTART.md)** - Get Mitch running in 10 minutes
- [Contributing](CONTRIBUTING.md) - How to help build Mitch
- [Development Guide](docs/DEVELOPMENT.md) - Technical details (coming soon)
- [Project Preferences](.agent/project-preferences.md) - Workflow and conventions

---

## Repository Structure

```
mitch-discord-bot/
├── .agent/                  # Agent workflow preferences
│   └── project-preferences.md
├── config/                  # Configuration templates
│   └── config.yaml.example
├── data/                    # Runtime data (database, logs)
├── docs/                    # Additional documentation
│   └── mitch.service        # SystemD service file
├── scripts/                 # Utility scripts
│   └── test_components.py   # Installation test script
├── src/                     # Source code
│   ├── bot.py              # Main Discord bot
│   ├── config_loader.py    # Configuration loading
│   └── logger.py           # Logging setup
├── tests/                   # Unit tests (future)
├── README.md               # You are here
├── QUICKSTART.md           # Quick setup guide
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # MIT License
├── requirements.txt        # Python dependencies
└── run.sh                  # Startup script
```

---

## Testing Your Installation

Before running in production, test your setup:

```bash
# Run component tests
python scripts/test_components.py

# Should show:
# ✓ Python version 3.9+
# ✓ Required directories exist
# ✓ Python dependencies installed
# ✓ Config file exists and loads
# ✓ Discord token configured
# ✓ Logger can create log files
# ✓ Bot modules can be imported
```

---

## Deployment Options

### Local Development (All Platforms)

```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
./run.sh
```

### Production (Linux with systemd)

```bash
# Copy service file
sudo cp docs/mitch.service /etc/systemd/system/

# Enable and start
sudo systemctl enable mitch
sudo systemctl start mitch

# Check status and logs
sudo systemctl status mitch
sudo journalctl -u mitch -f
```

See [QUICKSTART.md](QUICKSTART.md) for detailed deployment instructions.

---

## What's Next?

After v0.2.0 is deployed and stable:

**v0.3.0 - AI Integration**
- Connect to local Ollama instance
- Natural language understanding
- Context-aware responses
- Personality refinement

**v0.4.0 - Game Tracking**
- SQLite database setup
- Game library management
- Play history tracking
- Admin commands (!addgame, !played)

**v1.0.0 - Smart Suggestions**
- Player-count based filtering
- Recent play history consideration
- Voice channel awareness
- Full gaming buddy experience

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! This is a hobby project for a small gaming group, but if you find it useful, feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Fork and customize for your group

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Acknowledgments

Built with:
- [discord.py](https://discordpy.readthedocs.io/) - Discord API wrapper
- [Ollama](https://ollama.ai/) - Local LLM inference
- Love for gaming and good friends

---

**Status**: v0.2.0 complete - Production-ready Discord bot foundation

**Last Updated**: February 2026
