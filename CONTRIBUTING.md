# Contributing to Mitch Discord Bot

Thanks for your interest in contributing! This is a hobby project built for a small gaming group, but we welcome contributions from anyone who finds it useful.

---

## Project Philosophy

Before contributing, understand what Mitch is about:

- **Small scale**: Built for 5-15 people, not enterprise use
- **Casual personality**: Gaming buddy vibes, not corporate assistant
- **Self-hosted**: Runs on personal hardware, not cloud services
- **Simple**: Does a few things well rather than many things poorly

---

## How to Contribute

### Reporting Bugs

Found a bug? Here's how to report it:

1. **Check existing issues** - Someone might have already reported it
2. **Create a new issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, discord.py version)
   - Relevant logs (remove sensitive info like tokens!)

### Suggesting Features

Have an idea? Great! But first:

1. **Check the project scope** - Does it fit the "small gaming group" use case?
2. **Open an issue** to discuss before coding
3. **Explain the use case** - How would this help a gaming group?
4. **Consider complexity** - Is it worth the maintenance burden?

**Note:** Features that add significant complexity or move away from the "casual gaming buddy" vibe might not be accepted.

### Submitting Code

Ready to contribute code? Follow these steps:

#### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/mitch-discord-bot.git
cd mitch-discord-bot
git remote add upstream https://github.com/BigLangerStyle/mitch-discord-bot.git
```

#### 2. Create a Branch

Use the naming convention:

- **Features**: `feature/your-feature-name`
- **Bug fixes**: `fix/bug-description`
- **Documentation**: `docs/what-youre-documenting`

```bash
git checkout -b feature/voice-detection
```

#### 3. Make Your Changes

Follow these guidelines:

**Code Style:**
- Keep functions short and focused
- Use descriptive variable names (no `x`, `temp`, `data`)
- Add comments explaining **why**, not **what**
- Use type hints where helpful
- Follow PEP 8 (mostly - we're not strict)

**Testing:**
- Test your changes locally
- Run `scripts/test_components.py` if it exists
- Make sure the bot still starts and responds
- Test with real Discord server if possible

**Documentation:**
- Update README.md if you add features
- Add docstrings to new functions
- Update config.yaml.example if you add config options
- Include usage examples for new commands

#### 4. Commit Your Changes

Write clear, descriptive commit messages:

**Good:**
```
Add voice channel detection

- Monitor voice channels for online members
- Update context with voice state
- Fall back to server members if no voice activity
```

**Bad:**
```
fix stuff
updated code
changes
```

**Commit message format:**
```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how (the code shows how).

- Bullet points are okay
- Reference issues like #123 if relevant
```

#### 5. Push and Create Pull Request

```bash
git push origin feature/voice-detection
```

Then on GitHub:
1. Click "Compare & pull request"
2. Fill out the PR template (if we have one)
3. Explain what you changed and why
4. Link to any related issues

---

## Code Guidelines

### Python Standards

**Function length:** 
- Aim for under 50 lines
- If longer, consider breaking it up
- One function = one responsibility

**Error handling:**
- Components should never crash the bot
- Use try/except in critical sections
- Log errors, don't just swallow them
- Provide fallback responses when things fail

**Imports:**
```python
# Standard library
import sys
from typing import Optional

# Third-party
import discord
from discord.ext import commands

# Local
from personality import get_response
from game_tracker import GameTracker
```

### Personality Guidelines

Mitch's voice should be:
- Casual and conversational
- Like a gaming buddy, not an assistant
- Brief and to-the-point
- Honest when uncertain

**Good examples:**
```python
"hmm for 4 people, maybe Phasmophobia?"
"you guys just played that yesterday lol"
"not sure what the vibe is - competitive or co-op?"
```

**Bad examples:**
```python
"I'd be delighted to assist you! 😊"
"Based on my comprehensive analysis..."
"Here are 10 excellent options for your consideration"
```

### Database Guidelines

- Always use context managers for connections
- Commit after every write
- Handle unique constraint violations
- Don't leave connections open
- Keep schema simple

### Discord.py Best Practices

- Use `async with message.channel.typing()` for long operations
- Never block the event loop
- Handle rate limits gracefully
- Split messages over 2000 characters
- Check permissions before trying to send

---

## Development Workflow

### Branch Strategy

```
main
 ├── feature/voice-detection
 ├── feature/admin-commands
 └── fix/ollama-timeout
```

- `main` - Stable, released code
- Feature branches - New features
- Fix branches - Bug fixes

### Testing Before PR

1. Run the test suite (when it exists):
   ```bash
   python3 scripts/test_components.py
   ```

2. Test the bot manually:
   ```bash
   ./run.sh
   # In Discord, @mention the bot
   # Test your specific changes
   ```

3. Check logs for errors:
   ```bash
   tail -f data/mitch.log
   ```

### Review Process

- PRs need approval before merging
- Maintainers may request changes
- Be patient - this is a hobby project
- Discussion is welcome!

---

## AI-Assisted Development Workflow

This project uses a structured workflow for AI-assisted development with Claude. If you're using AI tools to help build features, follow these guidelines:

### Workflow Documentation

See `.agent/claude_workflow.md` for detailed workflow rules. Key principles:

**DO:**
- ✅ Keep context small and focused (only files being modified)
- ✅ Provide complete, final files (not diffs or snippets)
- ✅ Test changes on both development and deployment environments
- ✅ Use feature branches for all changes
- ✅ Run component tests before committing

**DON'T:**
- ❌ Upload full project zips to AI assistants
- ❌ Commit AI-generated code without testing it yourself
- ❌ Skip the testing phase
- ❌ Commit secrets or tokens (even in example files)

### Required Testing Before Commit

Every PR must pass these checks:

1. **Component Tests:**
   ```bash
   python scripts/test_components.py
   # Must show "All checks passed!"
   ```

2. **Manual Testing:**
   ```bash
   # Test locally first
   ./run.sh
   # Verify bot connects and responds to @mentions
   ```

3. **Deployment Testing (for significant changes):**
   ```bash
   # On MediaServer or test environment
   git pull
   sudo systemctl restart mitch
   sudo journalctl -u mitch -f
   # Verify no errors in logs
   ```

### Config Management

When adding new config options:

1. Update `config/config.yaml.example` with placeholder values
2. Document the new option in QUICKSTART.md
3. Never commit actual tokens or secrets
4. Use clear placeholder text like `YOUR_TOKEN_HERE`

---

## What NOT to Do

❌ **Don't add enterprise features** - This isn't for 1000+ user servers

❌ **Don't make Mitch formal** - Keep the casual gaming buddy vibe

❌ **Don't require cloud services** - Must work self-hosted

❌ **Don't add unnecessary dependencies** - Keep it lightweight

❌ **Don't break existing configs** - Backwards compatibility matters

❌ **Don't commit secrets** - No tokens, passwords, or API keys

---

## Questions?

- Open an issue for questions
- Check existing docs in `/docs`
- Read the project preferences in `.agent/project-preferences.md`

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License (same as the project).

---

**Thanks for contributing! Let's make Mitch awesome together. 🎮**
