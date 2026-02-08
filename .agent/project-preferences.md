# Agent Preferences for Mitch Discord Bot Project

## ðŸš¨ CRITICAL: Version Control Rules

**CURRENT VERSION: 1.0.0**

### DO NOT increment version without explicit user instruction

All features currently listed in the project as part of **v1.0.0** should remain in the v1.0.0 release.

**Do NOT create v1.0.1, v1.1.0, v2.0.0, etc. unless the user explicitly says to move to the next version.**

### When Adding New Features

#### âœ… CORRECT Approach:
- Keep version at 1.0.0 in all version-tracking files
- Add feature to existing version sections in CHANGELOG.md (if created)
- Update README.md with new features under current version
- Keep the same release date or update to current work date

#### âŒ WRONG Approach:
- Creating new version sections without explicit user instruction
- Incrementing version numbers spontaneously
- Creating new release tags without permission

### Current Development Status

**v1.0.0 - Complete:**
- [x] Discord bot with mention detection
- [x] Ollama integration (phi3:mini)
- [x] Game library database (SQLite)
- [x] Play history tracking
- [x] Casual gaming buddy personality
- [x] systemd service template
- [x] Testing utilities
- [x] Comprehensive documentation

**Future (Not Yet Scheduled):**
- [ ] Admin commands (!addgame, !played)
- [ ] Voice channel detection
- [ ] Reaction-based play tracking
- [ ] Steam library integration
- [ ] Game statistics dashboard

---

## ðŸŒ³ Git Workflow & Branch Strategy

**This project uses a simple, practical branching workflow.**

### Branch Structure

```
main
 â””â”€â”€ feature/voice-detection
 â””â”€â”€ feature/admin-commands
 â””â”€â”€ fix/ollama-timeout
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

## ðŸ“ Project Structure

```
mitch-discord-bot/
â”œâ”€â”€ .agent/                    (project preferences)
â”‚   â””â”€â”€ project-preferences.md
â”œâ”€â”€ .git/                      (version control)
â”œâ”€â”€ .gitignore
â”œâ”€â”€ LICENSE
â”œâ”€â”€ README.md
â”œâ”€â”€ QUICKSTART.md
â”œâ”€â”€ CONTRIBUTING.md
â”œâ”€â”€ GITHUB_SETUP.md
â”œâ”€â”€ config/
â”‚   â””â”€â”€ config.yaml.example
â”œâ”€â”€ data/                      (created at runtime)
â”‚   â”œâ”€â”€ mitch.db              (SQLite database)
â”‚   â””â”€â”€ mitch.log             (log file)
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ DEVELOPMENT.md
â”‚   â””â”€â”€ mitch.service
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ setup_games.py        (populate game library)
â”‚   â”œâ”€â”€ test_components.py    (test suite)
â”‚   â””â”€â”€ test_ai.py           (interactive AI tester)
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ bot.py               (main Discord bot)
â”‚   â”œâ”€â”€ ollama_client.py     (Ollama API integration)
â”‚   â”œâ”€â”€ personality.py       (Mitch's character)
â”‚   â”œâ”€â”€ game_tracker.py      (database operations)
â”‚   â””â”€â”€ config_loader.py     (configuration)
â”œâ”€â”€ tests/                    (future unit tests)
â”œâ”€â”€ requirements.txt
â””â”€â”€ run.sh
```

---

## ðŸ’» Development Workflow

### On Development Machine (Windows/Mac/Linux):
1. Edit code in your IDE (Cursor, VSCode, etc.)
2. Test locally if possible
3. Commit changes with meaningful messages
4. Push to GitHub

### On MediaServer (Linux Mint):
1. SSH into server
2. `cd ~/mitch-discord-bot`
3. `git pull`
4. `sudo systemctl restart mitch` (if running as service)
5. Check logs: `sudo journalctl -u mitch -f`

---

## ðŸ Python Development Standards

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

## ðŸ¤– AI Integration Guidelines

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

## ðŸ“Š Database Management

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

## ðŸ§ª Testing Strategy

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

## ðŸš¨ Git Management

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

## ðŸŽ¯ Discord Bot Best Practices

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

## ðŸ“¦ Deployment

### SystemD Service:
- Service file: `docs/mitch.service`
- Resource limits: 25% CPU quota, 2GB RAM
- Auto-restart on failure
- Logs to journald

### Updates:
```bash
# On MediaServer
cd ~/mitch-discord-bot
git pull
sudo systemctl restart mitch
sudo journalctl -u mitch -f  # Watch logs
```

---

## ðŸŽ­ Personality Guidelines

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
- "I'd be delighted to assist you! ðŸ˜Š"
- "Based on my comprehensive analysis..."
- "Here are 10 excellent options for your consideration"

---

## ðŸ“ Documentation Standards

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

## ðŸ”® Future Enhancements (Ideas to Keep in Mind)

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
- React âœ… to Mitch's suggestions when you play that game
- Automatically update play history
- Track suggestion accuracy

### Advanced Features:
- Steam library integration
- Machine learning for preferences
- Natural language game search
- Multi-server support

Keep code structure flexible to accommodate these!

---

## ðŸ“‹ Task Completion & File Handoff

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

## ðŸŽ® Gaming Group Context

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

## ðŸš€ Quick Reference

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

**Last Updated:** Initial version (v1.0.0)
**Project Status:** Production-ready, actively maintained
