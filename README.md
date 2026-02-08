# Mitch - Your Gaming Buddy Discord Bot

**Version:** 0.2.0 (In Progress)  
**Status:** Discord Bot Skeleton Complete - Bot Connects & Responds

---

## What is Mitch?

Mitch is a Discord bot that acts like your gaming buddy - not a corporate assistant. Built for small gaming groups (5-15 people), Mitch helps you figure out what to play when you're stuck in the "idk, what do you want to play?" loop.

### The Vision

Picture this: You and your friends hop into Discord voice. Someone asks, "what should we play?" Instead of the usual back-and-forth, you just @mention Mitch. He knows who's online, what you've played recently, and suggests something that actually fits your vibe.

No flashy commands. No enterprise features. Just a chill bot that helps you pick a game and get playing.

---

## Quick Start

**Prerequisites:**
- Python 3.9+
- Discord bot token ([Create one here](https://discord.com/developers/applications))

**Setup:**
```bash
# Clone the repo
git clone https://github.com/yourusername/mitch-discord-bot.git
cd mitch-discord-bot

# Install dependencies
pip install -r requirements.txt

# Configure the bot
cp config/config.yaml.example config/config.yaml
nano config/config.yaml  # Add your Discord bot token

# Run the bot
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

**v0.2.0 (Discord Bot Skeleton)** - 🏗️ In Progress
- Task 1: Configuration & Logging Foundation ✅ Complete
  - Config loader with YAML support
  - Rotating file logging system
  - Error handling utilities
  - Unit tests for config validation
- Task 2: Discord Bot Core ✅ Complete
  - Discord connection with proper intents
  - Mention detection and response
  - Hardcoded casual responses
  - Graceful error handling and shutdown
  - Unit tests for bot functionality
- Task 3: Database Schema & Game Library (Next)
- Task 4: Ollama Integration

**v1.0.0 (Full Release)** - 🎯 Goal
- Complete feature set
- Production-ready
- Deployed and tested

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions (coming in v0.2.0+).

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

- [Setup Guide](QUICKSTART.md) - How to run Mitch (v0.2.0+)
- [Contributing](CONTRIBUTING.md) - How to help build Mitch
- [Development Guide](docs/DEVELOPMENT.md) - Technical details (v0.2.0+)
- [Project Preferences](.agent/project-preferences.md) - Workflow and conventions

---

## Repository Structure

```
mitch-discord-bot/
├── .agent/                  # Agent workflow preferences
├── config/                  # Configuration templates
│   └── config.yaml.example
├── data/                    # Runtime data (database, logs)
├── docs/                    # Additional documentation
├── scripts/                 # Utility scripts (v0.2.0+)
├── src/                     # Source code
│   ├── bot.py              # Main Discord bot
│   ├── config_loader.py    # Configuration loading
│   ├── logger.py           # Logging setup
│   └── utils.py            # Error handling utilities
├── tests/                   # Unit tests
│   └── test_bot.py         # Bot functionality tests
├── README.md               # You are here
├── QUICKSTART.md           # Setup guide
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # MIT License
├── requirements.txt        # Python dependencies
└── run.sh                  # Startup script
```

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

**Status**: v0.2.0 in progress - Discord Bot Skeleton complete

**Last Updated**: February 2026
