# Changelog

All notable changes to Mitch Discord Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-02-14

### Fixed
- **Context Leakage in Casual Chat**: Conversation context was bleeding into casual responses, making Mitch sound like he was eavesdropping on group conversations. Updated AI prompt to only use context when directly relevant (e.g., acknowledging "thanks!") while ignoring unrelated chat history.
  - Updated `CASUAL_SYSTEM_PROMPT` in `src/personality.py`
  - Added explicit instructions to respond ONLY to the direct @mention
  - Added rule to IGNORE unrelated conversation history
  - Added examples of when context SHOULD be used (contextual "thanks!" acknowledgment)
  - Preserves contextual acknowledgments for relevant responses
  - Prevents incorporation of unrelated conversation history
  - Casual @mentions now get direct, clean responses

### Technical Details
- **Type**: Prompt engineering fix (no code logic changes)
- **Files Modified**: `src/personality.py`
- **Breaking Changes**: None
- **Migration**: None required (just restart bot)

## [1.2.0] - 2026-02-14

### Added - Documentation
- **docs/ARCHITECTURE.md**: Comprehensive component architecture documentation
  - High-level component overview with ASCII diagrams
  - Detailed explanation of each component (bot, personality, suggestion_engine, etc.)
  - Data flow diagrams for casual chat and game suggestions
  - Complete database schema with examples and relationships
  - Error handling strategy and fallback hierarchy
  - Performance considerations for modest hardware
  - Technology choices explained (Python, Ollama, SQLite, discord.py)
  - Future architecture planning
  
- **docs/TROUBLESHOOTING.md**: Complete troubleshooting guide
  - Quick diagnostics commands
  - Bot connection issues (token, permissions, intents)
  - Ollama/AI issues (timeouts, model not found, weird responses)
  - Database issues (locked, corrupted, empty library)
  - Game suggestion problems (cooldown, filtering, randomness)
  - Performance issues (memory, slow responses)
  - Deployment issues (systemd service problems)
  - Log analysis guide with specific grep commands
  - "Getting Help" section with what information to provide
  
- **docs/CONFIGURATION.md**: Detailed configuration reference
  - Every config option explained with type, default, recommended range
  - "WHY CHANGE" guidance for each setting
  - When/how to change settings based on use case
  - Examples and common values for different scenarios
  - Impact on performance and behavior
  - Five complete configuration examples (small group, public server, slow hardware, fast hardware, testing)
  - Validation commands and common config errors
  - Quick reference table

### Changed - Documentation
- **docs/DEVELOPMENT.md**: Complete rewrite from v0.1.0 placeholder
  - Development environment setup (prerequisites, installation, configuration)
  - Complete project structure with file-by-file explanations
  - Git workflow and branching strategy
  - Code style guidelines (PEP 8, comments, error handling, async/await)
  - Testing guide (component tests, interactive scripts, manual Discord testing)
  - Debugging techniques (debug mode, database inspection, Ollama testing)
  - Adding new features (examples: new database tables, admin commands)
  - Common development tasks (adding games, clearing history, personality tuning)
  - Performance optimization tips
  - Troubleshooting development issues
  
- **docs/mitch.service**: Enhanced systemd service file
  - Comprehensive inline comments explaining every setting
  - Hardware-specific tuning notes (MediaServer i3-3225)
  - Security hardening explanations
  - Resource limit reasoning (CPU, memory)
  - Clear instructions on what to change for your setup
  
- **config/config.yaml.example**: Enhanced configuration template
  - Updated version to 1.2.0
  - Added reference to docs/CONFIGURATION.md
  - Added "WHY CHANGE" guidance for every section
  - Tuning guides based on use case (library size, hardware, server type)
  - Examples of alternative values
  - Ollama section: Model alternatives, temperature tuning, timeout guidance
  - Suggestions section: Cooldown tuning by library size
  - Conversation section: Context message tuning by server activity
  - Rate limiting section: When to enable/disable
  
- **README.md**: Updated to v1.2.0
  - Added v1.2.0 release status
  - Updated status line to reflect professional documentation

### Documentation Improvements
- All documentation now professional and portfolio-ready
- Easy for new contributors to understand and modify project
- Comprehensive troubleshooting reduces support requests
- Every config option has clear explanation and tuning guidance
- Architecture clearly explained for maintainability

### Technical
- No code changes in v1.2.0 (documentation-only release)
- Created SCRIPT_HEADERS.md with templates for Python script docstrings
- Total new documentation: ~3,500 lines across 6 files

## [1.1.0] - 2025-02-13

### Added
- **Full Conversational AI**: Mitch now handles ALL @mentions with AI, not just game suggestions
- **Conversation Context Tracking**: Remembers last 5 messages per channel for natural conversation flow
- **`casual_response()` function**: New method in PersonalitySystem for handling casual chat
- **Rate Limiting**: Optional spam prevention (configurable, disabled by default)
- **Conversation Configuration**: New `conversation` section in config.yaml for context settings
- **Rate Limiting Configuration**: New `rate_limiting` section in config.yaml
- **Enhanced Logging**: Shows whether request was casual chat or game suggestion
- **Game Suggestion Randomization**: Shuffles filtered games for variety in suggestions

### Changed
- All casual @mentions now route through AI instead of hardcoded responses
- Conversation context passed to AI for more natural, contextual responses
- Updated personality prompts to handle both casual chat and game suggestions
- Casual responses have lighter polishing than game suggestions (300 char max vs 100)
- Bot.py now tracks conversation history per channel using deque
- Enhanced on_message handler to track messages for context
- Simplified prompt ending from verbose instruction to simple "Respond as Mitch:"
- Increased default Ollama timeout from 120s to 600s (better for cold starts)

### Fixed
- **Game Suggestions**: No longer suggests the same game repeatedly (now shuffles candidates)
- **AI Disclaimers**: Removed hallucinated Microsoft/AI self-references from responses
- **Instruction Leakage**: Fixed AI echoing conversation context and prompt instructions
- **Memory Efficiency**: Reduced RAM spikes from 97% to ~79% during AI generation (~75% improvement)
- **Casual Chat Bleeding**: Added explicit "NOT suggesting games" rule to casual prompt
- Casual interactions no longer feel robotic or repetitive
- "thanks!" and similar messages now get contextually appropriate responses
- Multi-turn conversations now flow naturally with memory of recent context
- Removed emoji patterns that were sneaking through (including :) emoticons)

### Technical
- Added `time` import for rate limiting timestamps
- Added `collections.defaultdict` and `deque` for conversation tracking
- Memory efficient: context limited to 5 messages per channel, resets on restart
- No database needed for context (in-memory only)
- Added `random.shuffle()` to suggestion_engine for game variety
- Enhanced response polishing with better artifact and disclaimer filtering
- Improved prompt structure to prevent context leakage

## [1.0.1] - 2025-02-09

### Fixed
- Fixed suggestion detection to use flexible keyword matching
- "what game" now properly triggers suggestion engine (was falling through to casual chat)
- Improved natural language understanding for game request detection

### Changed
- Suggestion detection now uses flexible `'what' in content AND ('game' OR 'play')` logic
- More permissive keyword matching allows natural phrasing

## [1.0.0] - 2025-02-08

### Added
- Smart game suggestion engine combining database + AI
- SQLite database with games, play_history, and suggestions tables
- Player count detection from online members
- Cooldown system (48 hours) to avoid repetitive suggestions
- Game library population script (scripts/setup_games.py)
- Ollama integration with phi3:mini model
- Personality system with casual gaming buddy character
- AI response polishing to maintain casual tone
- Graceful fallbacks when AI is unavailable
- Production-ready systemd service
- Comprehensive testing utilities
- Health check script for monitoring

### Documentation
- README.md with full project overview
- QUICKSTART.md for easy setup
- DEPLOYMENT.md for production deployment
- DATABASE.md explaining schema
- SUGGESTIONS.md explaining suggestion logic

## [0.2.0] - 2025-01-28

### Added
- Discord bot core with mention detection
- Configuration system with YAML support
- Rotating file logging
- SystemD service for deployment
- Hardcoded casual responses (replaced in v1.0.0)

## [0.1.0] - 2025-01-25

### Added
- Initial project structure
- Repository setup
- Project documentation framework
- Git workflow established

[1.2.0]: https://github.com/yourusername/mitch-discord-bot/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/yourusername/mitch-discord-bot/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/yourusername/mitch-discord-bot/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/yourusername/mitch-discord-bot/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/yourusername/mitch-discord-bot/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/mitch-discord-bot/releases/tag/v0.1.0
