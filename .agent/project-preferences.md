# Agent Preferences for Mitch Discord Bot Project

## 🚨 CRITICAL: Version Control Rules

**CURRENT VERSION: 1.0.0**

### DO NOT increment version without explicit user instruction

All features currently listed in the project as part of **v1.0.0** should remain in the v1.0.0 release.

**Do NOT create v1.0.1, v1.1.0, v2.0.0, etc. unless the user explicitly says to move to the next version.**

### When Adding New Features

#### ✅ CORRECT Approach:
- Keep version at 1.0.0 in all version-tracking files
- Add feature to existing version sections in CHANGELOG.md (if created)
- Update README.md with new features under current version
- Keep the same release date or update to current work date

#### ❌ WRONG Approach:
- Creating new version sections without explicit user instruction
- Incrementing version numbers spontaneously
- Creating new release tags without permission

### Current Development Status

**v0.2.0 - Complete (Working Bot Foundation):**
- [x] Discord bot with mention detection
- [x] Configuration loading (YAML)
- [x] Logging infrastructure
- [x] Hardcoded responses (no AI yet)
- [x] systemd service template
- [x] Testing utilities
- [x] Comprehensive documentation (QUICKSTART, CONTRIBUTING)
- [x] Deployment scripts (run.sh)

**v1.0.0 - In Progress:**
- [ ] Ollama integration (phi3:mini)
- [ ] Casual gaming buddy personality (AI-powered)
- [ ] Game library database (SQLite)
- [ ] Play history tracking
- [ ] Game suggestions based on who's online

**Future (Not Yet Scheduled):**
- [ ] Admin commands (!addgame, !played)
- [ ] Voice channel detection
- [ ] Reaction-based play tracking
- [ ] Steam library integration
- [ ] Game statistics dashboard

---

## 🌳 Git Workflow & Branch Strategy

**This project uses a simple, practical branching workflow.**

### Branch Structure

```
main
 └── release/v0.2.0 (complete)
 └── release/v1.0.0 (in progress)
      └── feature/ollama-integration
      └── feature/game-database
      └── feature/personality-system
```

### Workflow Rules

#### 1. **Main Branch**
- `main` contains the stable, released code
- All releases are tagged from main (e.g., `v1.0.0`, `v1.1.0`)
- Direct commits to main are fine for:
  - Documentation updates
  - README changes
  - Configuration tweaks
  - Quick fixes

#### 2. **Feature Branches**
For new features or significant changes:

```bash
git checkout main
git pull origin main
git checkout -b feature/voice-detection
# Work on feature
git commit -m "Add voice channel detection"
git push origin feature/voice-detection
# Create PR to main when ready
```

#### 3. **Bug Fix Branches**
For bugs that need fixing:

```bash
git checkout main
git checkout -b fix/ollama-timeout
# Fix the bug
git commit -m "Fix Ollama timeout issues"
git push origin fix/ollama-timeout
# Create PR to main
```

### Branch Naming Convention

**Feature branches:**
- Format: `feature/{descriptive-name}`
- Examples: `feature/voice-detection`, `feature/admin-commands`

**Bug fix branches:**
- Format: `fix/{descriptive-name}`
- Examples: `fix/ollama-timeout`, `fix/database-lock`

**Documentation branches:**
- Format: `docs/{descriptive-name}`
- Examples: `docs/installation-guide`, `docs/api-reference`

---

## 📁 Project Structure

```
mitch-discord-bot/
├── .agent/                    (project preferences)
│   ├── project-preferences.md
│   └── claude_workflow.md
├── .git/                      (version control)
├── .gitignore
├── LICENSE
├── README.md
├── QUICKSTART.md
├── CONTRIBUTING.md
├── GITHUB_SETUP.md
├── config/
│   └── config.yaml.example
├── data/                      (created at runtime)
│   ├── mitch.db              (SQLite database)
│   └── mitch.log             (log file)
├── docs/
│   ├── DEVELOPMENT.md
│   └── mitch.service
├── scripts/
│   ├── setup_games.py        (populate game library)
│   ├── test_components.py    (test suite)
│   └── test_ai.py           (interactive AI tester)
├── src/
│   ├── bot.py               (main Discord bot)
│   ├── ollama_client.py     (Ollama API integration)
│   ├── personality.py       (Mitch's character)
│   ├── game_tracker.py      (database operations)
│   ├── config_loader.py     (configuration)
│   ├── logger.py            (logging setup)
│   └── utils.py             (utilities)
├── tests/                    (unit tests)
│   ├── test_config.py
│   └── test_bot.py
├── requirements.txt
└── run.sh
```

---

## 💻 Development Workflow

### On Development Machine (Windows/Mac/Linux):
1. Edit code in your IDE (Cursor, VSCode, etc.)
2. Test locally if possible
3. Commit changes with meaningful messages
4. Push to GitHub

### On MediaServer (Linux Mint):
1. SSH into server
2. `cd ~/git/mitch-discord-bot`
3. `git pull`
4. `sudo systemctl restart mitch` (if running as service)
5. Check logs: `sudo journalctl -u mitch -f`

---

## 🐍 Python Development Standards

### Code Style:
- Keep functions short and focused
- Use descriptive variable names
- Add comments for complex logic
- Use type hints where helpful

### Error Handling:
- Components should never crash the bot
- Catch exceptions, log errors, continue running
- Use try/except in all critical sections
- Provide fallback responses when AI fails

### Comments:
- Explain **WHY**, not just WHAT
- Document assumptions and edge cases
- Reference Discord.py or Ollama docs when relevant

---

## 🤖 AI Integration Guidelines

### Ollama Configuration:
- Default model: `phi3:mini` (lightweight, CPU-friendly)
- Temperature: 0.8 (balanced creativity)
- Max tokens: 300 (keeps responses concise)
- Timeout: 60 seconds

### Prompt Engineering:
- System prompt defines core personality
- Context includes: player count, recent games, requester name
- Keep prompts concise for faster inference
- Always include examples of good vs bad responses

### Response Handling:
- Polish AI responses to remove corporate language
- Strip excessive punctuation
- Remove emojis (Mitch doesn't use them)
- Provide fallbacks if AI is slow or fails

---

## 📊 Database Management

### SQLite Schema:
- `games` table: Game library with player counts and categories
- `play_history` table: When games were played
- `suggestions` table: What Mitch suggested (for analytics)

### Best Practices:
- Always use context managers for DB connections
- Commit after every write operation
- Handle unique constraint violations gracefully
- Backup `data/mitch.db` regularly

---

## 🧪 Testing Strategy

### Automated Tests:
- Run `scripts/test_components.py` before deploying
- Tests: imports, database, Ollama connection, personality

### Manual Testing:
- Use `scripts/test_ai.py` for interactive prompt testing
- Test with real Discord server before production
- Monitor logs during initial deployment

### Integration Tests:
- Test @mention detection
- Test with various player counts
- Test when Ollama is slow/offline
- Test with empty game library

---

## 🚨 Git Management

**CRITICAL: User manages Git separately**

Claude should:
- **NEVER** run git commands (`git init`, `git commit`, `git push`, etc.)
- **NEVER** create branches
- **NEVER** manage version control

The user handles all Git operations in their own environment (Cursor, terminal, etc.).

Claude's job is to:
1. Create/modify source files
2. Update documentation
3. Present files ready for user to commit

---

## 🎯 Discord Bot Best Practices

### Message Handling:
- Always use `async with message.channel.typing()` for long operations
- Split messages over 2000 characters
- Handle rate limits gracefully
- Never block the event loop

### Permissions:
- Minimum required: Read Messages, Send Messages, Read Message History
- Enable "Message Content Intent" in Discord Developer Portal
- Don't request unnecessary permissions

### Error Messages:
- Keep error messages friendly and casual
- Don't expose technical details to users
- Log full errors for debugging

---

## 📦 Deployment

### SystemD Service:
- Service file: `docs/mitch.service`
- Resource limits: 25% CPU quota, 2GB RAM
- Auto-restart on failure
- Logs to journald

### Updates:
```bash
# On MediaServer
cd ~/git/mitch-discord-bot
git pull
sudo systemctl restart mitch
sudo journalctl -u mitch -f  # Watch logs
```

---

## 🎭 Personality Guidelines

Mitch should sound like:
- A gaming buddy, not a corporate assistant
- Casual and conversational
- Uses gaming slang appropriately
- Honest when uncertain
- Brief and to-the-point

Mitch should NOT:
- Use excessive emojis
- Be overly formal or polite
- Apologize excessively
- Write long explanations
- Try too hard to be funny

**Good examples:**
- "hmm for 4 people, maybe Phasmophobia?"
- "you guys just played that yesterday lol"
- "not sure what the vibe is - competitive or co-op?"

**Bad examples:**
- "I'd be delighted to assist you! 😊"
- "Based on my comprehensive analysis..."
- "Here are 10 excellent options for your consideration"

---

## 📝 Documentation Standards

### README.md:
- Keep concise and scannable
- Focus on getting started quickly
- Link to detailed docs for deep dives

### Code Comments:
- Explain complex logic
- Document assumptions
- Note API quirks or workarounds

### Commit Messages:
**Good:**
```
Add voice channel detection

- Monitors voice channels for online members
- Updates context with voice state
- Falls back to server members if no voice activity
```

**Bad:**
```
fix stuff
updated code
changes
```

---

## 🔮 Future Enhancements (Ideas to Keep in Mind)

### Admin Commands (v1.1.0+):
- `!addgame` - Add game to library
- `!played` - Mark game as played
- `!games` - List all games
- `!stats` - Show play statistics

### Voice Channel Integration:
- Auto-detect who's in voice
- Adjust suggestions based on voice state
- Monitor voice channel changes

### Reaction Tracking:
- React ✅ to Mitch's suggestions when you play that game
- Automatically update play history
- Track suggestion accuracy

### Advanced Features:
- Steam library integration
- Machine learning for preferences
- Natural language game search
- Multi-server support

Keep code structure flexible to accommodate these!

---

## 📋 Task Completion & File Handoff

When creating tasks for new features:

### Always Include:
1. **Task description** - What needs to be done
2. **Files to modify** - Specific Python files
3. **Expected outcome** - How to verify it works
4. **Testing steps** - How to test the feature

### Files Commonly Modified:
- `src/bot.py` - Core bot logic
- `src/personality.py` - Mitch's responses
- `src/game_tracker.py` - Database operations
- `README.md` - Documentation updates

### Don't Include:
- Full project zips (causes context issues)
- Database files
- Log files
- Environment-specific configs

---

## 🎮 Gaming Group Context

This bot is built for a small gaming group, not enterprise use. This means:
- **Small scale**: 5-15 people, not hundreds
- **Casual use**: Suggestions a few times a week
- **Self-hosted**: Running on personal hardware
- **Customizable**: Easy to tweak for specific group preferences

Design decisions should prioritize:
1. **Simplicity** over enterprise features
2. **Personality** over formality
3. **Reliability** over fancy features
4. **Easy customization** over rigid structure

---

## 🚀 Quick Reference

**Test everything:**
```bash
python3 scripts/test_components.py
```

**Populate games:**
```bash
python3 scripts/setup_games.py populate
```

**Run bot:**
```bash
./run.sh
```

**Check logs (if service):**
```bash
sudo journalctl -u mitch -f
```

**Test AI responses:**
```bash
python3 scripts/test_ai.py
```

---

**Last Updated:** February 2026 (v0.2.0 complete, v1.0.0 in progress)
**Project Status:** Active development toward v1.0.0
