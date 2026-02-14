# Changelog

All notable changes to the Mitch Discord Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.2] - 2026-02-14

### Fixed
- **Suggestion Variety**: Removed implicit bias toward Deep Rock Galactic in AI prompts. Prompt examples were showing DRG twice, causing the AI to favor it in suggestions. Changed to generic placeholders to ensure fair game variety.
  - Updated suggestion prompt in `src/suggestion_engine.py`
  - Investigation confirmed filtering/cooldown/randomization working correctly
  - Simple one-line prompt fix resolved the issue

### Investigation
- Investigated Deep Rock Galactic appearing too frequently in suggestions
- Root cause: Prompt engineering bias (DRG mentioned in examples twice)
- Not a filtering, database, or cooldown issue - all working correctly

---

## [1.2.1] - 2026-02-14

### Fixed
- **Context Leakage in Casual Chat**: Conversation context was bleeding into casual responses, making Mitch sound like he was eavesdropping on group conversations. Updated AI prompt to only use context when directly relevant (e.g., acknowledging "thanks!") while ignoring unrelated chat history.
  - Updated `CASUAL_SYSTEM_PROMPT` in `src/personality.py`
  - Preserves contextual acknowledgments for relevant responses
  - Prevents incorporation of unrelated conversation history
  - Casual @mentions now get direct, clean responses

### Technical Details
- **Type**: Prompt engineering fix (no code logic changes)
- **Files Modified**: `src/personality.py`
- **Breaking Changes**: None
- **Migration**: None required (just restart bot)

---

## [1.2.0] - 2026-02-14

### Added
- **Comprehensive Documentation** (~3,500 lines of professional documentation)
  - `docs/ARCHITECTURE.md` - Complete system architecture, component overview, data flows
  - `docs/TROUBLESHOOTING.md` - Common issues with diagnostic commands and solutions
  - `docs/CONFIGURATION.md` - Deep-dive on every config option with tuning guidance
  - `UNINSTALL.md` - Complete uninstallation guide

### Changed
- **Enhanced Existing Documentation**
  - `docs/DEVELOPMENT.md` - Complete rewrite from v0.1.0 placeholder (~550 lines)
  - `docs/mitch.service` - Added comprehensive inline comments for all settings
  - `config/config.yaml.example` - Enhanced with "WHY CHANGE" guidance throughout
  - `README.md` - Updated to v1.2.0
  - `CHANGELOG.md` - Comprehensive formatting and organization

### Documentation Improvements
- Portfolio-ready quality documentation
- Self-service troubleshooting capabilities
- Contributor-friendly onboarding
- Complete configuration reference
- Hardware-specific tuning notes for MediaServer

### Technical Details
- **Type**: Documentation-only release (no code changes)
- **Files Modified**: 9 documentation files (4 new, 5 enhanced)
- **Breaking Changes**: None
- **Migration**: None required

---

## [1.1.0] - 2026-02-13

### Added
- **Full Conversational AI**: All @mentions now route through AI for natural conversations
  - `casual_response()` function for general chat interactions
  - Smart routing: detects game requests vs casual conversation
  - Conversation context tracking (last 5 messages per channel)
  - Natural contextual responses ("thanks!" → acknowledges what they're thanking for)

- **Optional Rate Limiting**
  - Configurable spam prevention (disabled by default)
  - Per-user cooldown between @mentions
  - Perfect for small friend groups

### Changed
- **Game Suggestion Variety**: Shuffles filtered games before presenting to AI
  - Prevents "Deep Rock Galactic every time" syndrome
  - `random.shuffle()` in `suggestion_engine.py`

- **Enhanced Response Quality**
  - Removes AI disclaimers and self-references
  - Filters out hallucinated company attributions
  - Prevents instruction leakage from prompts
  - Better immersion in casual gaming buddy role

- **Configuration Updates**
  - New `conversation` section (context_messages, casual_max_length)
  - New `rate_limiting` section (enabled, cooldown_seconds, message)
  - Increased default timeout to 600s for better cold-start handling

### Fixed
- **Memory Optimization** ⭐ HUGE WIN
  - Reduced RAM spikes from 97% → ~79% during AI generation
  - ~75% reduction in memory spike (2GB → 0.5GB)
  - HomeSentry alerts eliminated completely
  - Achieved through cleaner prompts and better Ollama caching

- **Casual Chat Not Suggesting Games**
  - Added explicit "NOT suggesting games" rule to casual prompt
  - Prevents "say something funny" → "how about Tetris?" responses
  - Clear separation between chat modes

### Technical Details
- **Files Modified**: `src/bot.py`, `src/personality.py`, `src/suggestion_engine.py`, `config/config.yaml.example`
- **New Features**: Conversation tracking, rate limiting (optional)
- **Performance**: Significant memory optimization
- **Breaking Changes**: None (backwards compatible)

---

## [1.0.1] - 2026-02-09

### Fixed
- **Critical: Suggestion Detection**: Core feature was broken - users asking for game suggestions were being treated as casual conversation
  - "what game could we play?" → Now correctly detected as suggestion request ✓
  - "give me a good co-op game" → Now correctly detected as suggestion request ✓
  - "any suggestions?" → Now correctly detected as suggestion request ✓

### Changed
- **Flexible Trigger Detection**: Changed from exact phrase matching to keyword combinations
  - Now matches: ('what' + 'play/game'), ('suggest/recommend' + 'game'), ('give me' + 'game/suggestion'), 'any suggestions'
  - More natural language understanding
  - Reduced false negatives

- **Clearer AI Prompts**: AI explicitly instructed to list specific game names
  - AI now provides concrete game suggestions instead of vague responses
  - Better instruction clarity prevents "hey peeps" type responses

- **Better Logging**: Added debug output for suggestion detection
  - "✓ Detected game suggestion request"
  - Shows filtered games list
  - Tracks suggestion generation timing

### Technical Details
- **Branch**: `fix/suggestion-detection`
- **Files Modified**: `src/bot.py`, `src/suggestion_engine.py`, `CHANGELOG.md`
- **Type**: Critical bug fix
- **Impact**: Restores primary bot functionality

---

## [1.0.0] - 2026-02-08

### Added
- **Ollama Integration & AI Personality**
  - `src/ollama_client.py` - HTTP client for local Ollama API
  - `src/personality.py` - Gaming buddy personality with casual tone
  - Two-tier response polishing (light for chat, strict for suggestions)
  - Fallback responses when AI unavailable

- **Database & Game Tracking**
  - `src/game_tracker.py` - SQLite database operations
  - Complete schema: games, play_history, suggestions tables
  - Foreign keys with CASCADE/SET NULL
  - Performance indexes and WAL mode
  - `scripts/setup_games.py` - Game library management
  - Populated with 10 actual games

- **Smart Suggestions Logic**
  - `src/suggestion_engine.py` - AI + database suggestion system
  - Player count detection from online members
  - Game filtering by player count + 48h cooldown
  - Recent suggestion tracking (5 min cooldown)
  - Context-aware AI responses
  - Database recording for analytics

- **Production Polish & Testing**
  - Enhanced test suite (11 comprehensive tests)
  - Production health monitoring (`scripts/health_check.py`)
  - Production-ready systemd service with resource limits
  - Complete deployment guide (`docs/DEPLOYMENT.md`)
  - Full version history (CHANGELOG.md)

### Changed
- **Updated from v0.2.0 hardcoded responses** to full AI-powered system
- Integrated Ollama (phi3:mini) for all bot responses
- Added comprehensive database for game tracking
- Production deployment with systemd service

### Technical Details
- **Branch**: Multiple feature branches merged to `release/v1.0.0`
- **Files Created**: 8 new modules, 6 new scripts, 3 new docs
- **Testing**: All 11 component tests passing on MediaServer
- **Python**: 3.8.10 compatibility verified
- **Performance**: 3-20s AI responses (acceptable for hardware)

---

## [0.2.0] - 2026-02-08

### Added
- **Discord Bot Skeleton**
  - `src/bot.py` - Main bot with event handlers (on_ready, on_message)
  - @mention detection
  - Hardcoded casual responses (5 variations)
  - Typing indicators
  - Clean shutdown handling

- **Configuration & Logging Foundation**
  - `src/config_loader.py` - YAML config loading and validation
  - `src/logger.py` - Rotating file handler
  - `src/utils.py` - Error handling utilities
  - Comprehensive unit tests (13 tests, all passing)

- **Database Foundation**
  - `src/game_tracker.py` - SQLite schema creation
  - Empty schema ready for v1.0.0 implementation

- **Deployment & Documentation**
  - `docs/mitch.service` - systemd service file
  - `QUICKSTART.md` - Comprehensive setup guide
  - `scripts/test_components.py` - Testing utility (7 validation checks)
  - `run.sh` - Startup script
  - `.gitignore` - Secrets management

### Changed
- **Updated README.md** to mark v0.2.0 as complete
- **Updated CONTRIBUTING.md** with AI-assisted workflow
- **Updated requirements.txt** to support Python 3.13+

### Technical Details
- **Branch**: Multiple feature branches merged to `release/v0.2.0`
- **Testing**: Local (Windows Python 3.14.3), MediaServer (Linux Mint Python 3.8.10)
- **Deployment**: Successfully tested on MediaServer
- **Migration**: Python 3.9 venv setup on MediaServer

---

## [0.1.0] - 2026-02-07

### Added
- **Initial Repository Structure**
  - Directory layout (src/, config/, docs/, scripts/, tests/)
  - Core documentation (README.md, CONTRIBUTING.md, QUICKSTART.md placeholder)
  - `.agent/project-preferences.md` - Workflow documentation
  - `.agent/claude_workflow.md` - AI-assisted development patterns
  - `.gitignore`, LICENSE (MIT), requirements.txt
  - `config/config.yaml.example` template

- **Documentation**
  - Project vision and purpose
  - Target audience (small gaming groups)
  - Tech stack overview
  - Contribution guidelines
  - GitHub setup guide

### Technical Details
- **Type**: Repository structure only (no implementation)
- **Purpose**: Professional foundation for development
- **Files**: 16 placeholder and documentation files

---

## Future Versions

Potential enhancements for consideration:

### Possible v1.3.0+ Features
- Admin commands (!addgame, !played, !games, !stats)
- Voice channel detection (auto-detect who's in voice)
- Reaction-based tracking (✅ to mark game as played)
- Steam library integration
- Statistics dashboard
- Team Captain personality enhancement (90s lifeguard hero vibe)

### Under Consideration
- Multi-server support
- Natural language game search
- Machine learning for preference learning
- Advanced analytics and reporting

---

**Note**: Version numbering follows [Semantic Versioning](https://semver.org/):
- **Major version** (x.0.0): Breaking changes or major features
- **Minor version** (0.x.0): New features, backwards compatible
- **Patch version** (0.0.x): Bug fixes, backwards compatible
