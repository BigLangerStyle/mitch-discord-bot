# Changelog

All notable changes to Mitch Discord Bot are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-02-09

### Fixed

**Suggestion Detection** - Fixed critical bug where game requests weren't recognized
- Replaced strict phrase matching with flexible keyword detection
- Now recognizes natural variations: "what game could we play", "give me a good co-op game", "any suggestions?"
- Previously only matched exact phrases like "what should we play"

**AI Prompt Clarity** - Strengthened prompt to ensure specific game suggestions
- AI now explicitly instructed to name specific games from available list
- Added clear examples of good vs bad responses in prompt
- Reduced vague responses like "hey peeps" or "what do you like"

**Logging Improvements** - Added debug logging for production troubleshooting
- Bot now logs whether message was detected as suggestion request or casual chat
- Suggestion engine logs filtered game list for debugging
- Makes production diagnosis much easier

### Technical Details

**What Changed in `src/bot.py`:**
- Replaced `any(phrase in content_lower)` with flexible keyword matching
- Now checks for keyword combinations: `'what' + 'play'`, `'suggest' + 'game'`, `'give me' + 'game'`, etc.
- Added clear log messages: `"✓ Detected game suggestion request"` vs `"Handling as casual conversation"`

**What Changed in `src/suggestion_engine.py`:**
- Enhanced AI prompt with explicit "AVAILABLE GAMES (choose from these ONLY)" section
- Added clear examples of good vs bad responses
- Prompt now says "Respond NOW with specific game names" to force concrete suggestions
- Added logging of filtered game list for debugging

**Before Fix (v1.0.0):**
```
User: "what game could we play?"
Log: "Handling as casual conversation"  ❌
Bot: "hey what do u wanna play tonight?"  ❌
```

**After Fix (v1.0.1):**
```
User: "what game could we play?"
Log: "✓ Detected game suggestion request"  ✓
Log: "Generating suggestion for 4 players"  ✓
Log: "Games: ['Deep Rock Galactic', 'Overcooked 2', ...]"  ✓
Bot: "how about Deep Rock Galactic or Lethal Company? both good for 4"  ✓
```

---

## [1.0.0] - 2026-02-08

### Added

**AI Integration** - Natural language powered by local Ollama
- Ollama integration with phi3:mini model
- Casual gaming buddy personality
- Response polishing to remove corporate language
- Graceful fallbacks when AI is unavailable or slow
- Configurable temperature, max tokens, and timeout

**Game Database** - SQLite-based game library and history
- Game library with player count ranges and categories
- Play history tracking with timestamps
- Suggestion history for future analytics
- Automatic database creation and migrations
- WAL mode enabled for better concurrency
- Proper indexes for performance

**Smart Suggestions** - Context-aware game recommendations
- Filters games by current player count
- Respects cooldown period (48h default, configurable)
- Prevents repetition (5min suggestion cooldown)
- Considers recent play history
- Explains suggestions naturally
- Handles edge cases (empty library, all games in cooldown)

**Testing and Validation** - Comprehensive test suite
- `test_components.py` - Full system validation
- `test_ai.py` - Interactive AI testing
- `test_database.py` - Database operation testing
- `test_suggestions.py` - Suggestion engine testing
- `health_check.py` - Production health monitoring
- `setup_games.py` - Game library management

**Documentation** - Complete project documentation
- README.md - Project overview and features
- QUICKSTART.md - 10-minute setup guide
- DEPLOYMENT.md - Production deployment guide
- CONTRIBUTING.md - Development workflow
- DATABASE.md - Database schema and usage
- SUGGESTIONS.md - Suggestion algorithm explanation
- CHANGELOG.md - Version history (this file)

**Production Deployment** - Ready for production use
- systemd service template with resource limits
- Auto-restart on failure with rate limiting
- Security hardening (NoNewPrivileges, PrivateTmp, etc.)
- Proper logging to journald
- Health monitoring support

### Changed

- Replaced hardcoded responses with AI-generated responses
- Enhanced systemd service with better restart policy and resource limits
- Improved error handling throughout codebase
- Updated documentation for production readiness

### Technical Details

**Stack:**
- Python 3.9+
- discord.py 2.x for Discord API
- Ollama (phi3:mini model) for AI inference
- SQLite3 with WAL mode for data storage
- systemd for service management

**Hardware Requirements:**
- Linux server (tested on Linux Mint)
- Python 3.9 or higher
- 2GB RAM available
- ~100MB disk space
- CPU-only inference (no GPU required)

**Performance Baseline (MediaServer - i3-3225, 8GB RAM):**
- AI Response Time: 3-5 seconds average (1.5-20s range)
- Database Queries: < 1ms
- Memory Usage: 100-200MB
- CPU Usage: 5-10% idle, 20-50% during AI generation

---

## [0.2.0] - 2026-02-07

### Added

**Discord Bot Core** - Basic bot infrastructure
- Mention detection (@Mitch triggers responses)
- Hardcoded casual responses for testing
- SystemD service template
- Component testing script

**Configuration System** - YAML-based configuration
- Config loader with validation
- Environment-based config support
- Secure token management
- Example config file

**Logging System** - Production-ready logging
- Rotating file logging
- Configurable log levels
- Both file and console output
- Proper log formatting

### Technical Details

- Basic bot infrastructure complete
- Ready for AI and database integration
- Tested on both Windows and Linux Mint

---

## [0.1.0] - 2026-02-06

### Added

**Repository Foundation** - Project structure and conventions
- Directory structure established
- Core documentation (README, CONTRIBUTING, QUICKSTART)
- Git workflow defined
- License (MIT)
- .gitignore for Python projects
- GitHub setup documentation

### Technical Details

- Project conventions documented
- Development workflow established
- Ready for implementation

---

## Release Notes

### v1.0.1 - Critical Bug Fix 🔧

**This patch fixes a critical bug in v1.0.0** where the bot wasn't detecting game suggestion requests properly.

#### What Was Broken

In v1.0.0, Mitch would treat almost ALL messages as casual conversation instead of game suggestions:
- ❌ "what game could we play" → casual chat (should be suggestion)
- ❌ "give me a good co-op game" → casual chat (should be suggestion)
- ❌ "any suggestions?" → casual chat (should be suggestion)

Only exact phrase matches like "what should we play" worked.

#### What's Fixed

Now recognizes natural language variations:
- ✅ "what game could we play" → suggestion ✓
- ✅ "what game should we play tonight" → suggestion ✓
- ✅ "give me a good game" → suggestion ✓
- ✅ "suggest a co-op game" → suggestion ✓
- ✅ "any suggestions?" → suggestion ✓
- ✅ "recommend a game for us" → suggestion ✓

AI also gives more specific game names instead of vague responses.

#### Upgrading from v1.0.0

```bash
# 1. Pull latest code
git pull origin main

# 2. Restart bot
sudo systemctl restart mitch

# 3. Test in Discord
@Mitch what game could we play?
# Should now get actual game suggestions!

# 4. Check logs to verify
sudo journalctl -u mitch -f
# Should see "✓ Detected game suggestion request"
```

No config changes needed - this is a pure bug fix.

---

### v1.0.0 - Full Production Release 🎉

**Mitch is now production-ready!** This release includes everything needed to deploy and run Mitch in a production environment.

#### What You Can Do Now

- **Get smart game suggestions** - "@Mitch what should we play?"
- **Natural conversations** - Chat casually with Mitch
- **Automated tracking** - Play history recorded automatically
- **Reliable operation** - Runs as systemd service with auto-restart
- **Easy deployment** - Complete deployment guide included

#### What Works

✅ AI-powered responses using local Ollama (phi3:mini)  
✅ Game library database with SQLite  
✅ Smart suggestions filtered by player count  
✅ Cooldown system to avoid repetition  
✅ Play history tracking  
✅ Comprehensive testing suite  
✅ Production deployment as systemd service  
✅ Health monitoring  
✅ Complete documentation  

#### Known Limitations (v1.0.0)

These are intentional limitations for v1.0.0 - core functionality is the focus:

- **Player count** - Estimated from online members (no voice channel detection yet)
- **No admin commands** - Can't manually add games or mark plays via Discord
- **No reaction tracking** - Can't mark plays by reacting to suggestions
- **No Steam integration** - Game library is manual
- **English only** - No multi-language support

These limitations may be addressed in future versions if there's demand.

#### Performance Notes

- **Response Time**: 3-20 seconds depending on system load (acceptable for Discord)
- **Hardware**: Designed for modest hardware (i3-3225, 8GB RAM)
- **CPU-only**: No GPU required (phi3:mini is lightweight)
- **Memory**: Uses 100-200MB normally (under 2GB limit)

#### Upgrading from v0.2.0

If you're upgrading from v0.2.0:

1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama:**
   ```bash
   # Visit https://ollama.ai for installation
   ollama pull phi3:mini
   ```

4. **Update config:**
   ```bash
   # Add ollama and suggestions sections to config.yaml
   cp config/config.yaml config/config.yaml.backup
   # Merge new sections from config.yaml.example
   ```

5. **Setup game library:**
   ```bash
   python3 scripts/setup_games.py populate
   ```

6. **Run tests:**
   ```bash
   python3 scripts/test_components.py
   python3 scripts/health_check.py
   ```

7. **Update service:**
   ```bash
   sudo cp docs/mitch.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl restart mitch
   ```

8. **Verify:**
   ```bash
   sudo journalctl -u mitch -f
   # Test in Discord: @Mitch what should we play?
   ```

---

## What's Next?

**v1.0.1 was a critical bug fix.** v1.0.0 established core functionality done right. Future versions may add:

### Potential v1.1.0 Features (If Requested)

- **Admin Commands** - `!addgame`, `!played`, `!games`, `!stats`
- **Voice Channel Detection** - Priority suggestions based on who's in voice
- **Reaction Tracking** - React ✅ to suggestions when you play that game
- **Better Analytics** - Suggestion accuracy, most played games, etc.

### Potential v2.0.0 Features (If Requested)

- **Steam Integration** - Auto-import games from Steam libraries
- **Multi-Server Support** - Run one bot across multiple Discord servers
- **Web Dashboard** - View stats and manage games via web UI
- **Advanced Suggestions** - Machine learning for better recommendations

**Current focus:** Ensure v1.0.1 is rock-solid and meets user needs before adding extras.

---

## Feedback and Contributions

- **Bug Reports**: [GitHub Issues](https://github.com/yourusername/mitch-discord-bot/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/yourusername/mitch-discord-bot/issues)
- **Contributions**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0) - Incompatible changes
- **MINOR** version (1.1.0) - New features, backwards compatible
- **PATCH** version (1.0.1) - Bug fixes, backwards compatible

---

**Thank you for using Mitch! Now go play some games!** 🎮
