# Changelog

All notable changes to Mitch Discord Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-02-13

### Added
- **Full Conversational AI**: Mitch now handles ALL @mentions with AI, not just game suggestions
- **Conversation Context Tracking**: Remembers last 5 messages per channel for natural conversation flow
- **`casual_response()` function**: New method in PersonalitySystem for handling casual chat
- **Rate Limiting**: Optional spam prevention (configurable, disabled by default)
- **Conversation Configuration**: New `conversation` section in config.yaml for context settings
- **Rate Limiting Configuration**: New `rate_limiting` section in config.yaml
- **Enhanced Logging**: Shows whether request was casual chat or game suggestion

### Changed
- All casual @mentions now route through AI instead of hardcoded responses
- Conversation context passed to AI for more natural, contextual responses
- Updated personality prompts to handle both casual chat and game suggestions
- Casual responses have lighter polishing than game suggestions (300 char max vs 100)
- Bot.py now tracks conversation history per channel using deque
- Enhanced on_message handler to track messages for context

### Fixed
- Casual interactions no longer feel robotic or repetitive
- "thanks!" and similar messages now get contextually appropriate responses
- Multi-turn conversations now flow naturally with memory of recent context

### Technical
- Added `time` import for rate limiting timestamps
- Added `collections.defaultdict` and `deque` for conversation tracking
- Memory efficient: context limited to 5 messages per channel, resets on restart
- No database needed for context (in-memory only)

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

[1.1.0]: https://github.com/yourusername/mitch-discord-bot/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/yourusername/mitch-discord-bot/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/yourusername/mitch-discord-bot/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/yourusername/mitch-discord-bot/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/mitch-discord-bot/releases/tag/v0.1.0
