# Mitch Database Schema

Complete documentation for Mitch's SQLite database structure and usage.

---

## Overview

Mitch uses SQLite for local data storage. The database stores:
- **Game Library**: All games your group owns
- **Play History**: When games were played and by how many people
- **Suggestions**: What Mitch suggested and whether it was accepted

**Database Location**: `data/mitch.db` (configurable in `config/config.yaml`)

**Features**:
- Lightweight (SQLite, no server needed)
- ACID compliant (safe concurrent access)
- WAL mode enabled (better performance)
- Foreign key constraints enforced
- Indexed for fast queries

---

## Database Schema

### Table: `games`

Stores the game library with player counts and metadata.

```sql
CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    min_players INTEGER DEFAULT 1,
    max_players INTEGER DEFAULT 10,
    category TEXT,
    tags TEXT,  -- JSON array stored as text
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `name`: Game name (unique, case-insensitive)
- `min_players`: Minimum supported players
- `max_players`: Maximum supported players
- `category`: Game category (e.g., "co-op", "party", "competitive")
- `tags`: JSON array of tags (e.g., `["horror", "survival"]`)
- `added_date`: When the game was added to library

**Indexes**:
```sql
CREATE INDEX idx_games_players ON games(min_players, max_players);
```

---

### Table: `play_history`

Tracks when games were played.

```sql
CREATE TABLE play_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    played_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    player_count INTEGER,
    notes TEXT,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `game_id`: Reference to game in library
- `played_date`: When the game was played
- `player_count`: How many players participated
- `notes`: Optional notes about the session

**Foreign Keys**:
- `game_id` → `games(id)` with `ON DELETE CASCADE`
  - If a game is deleted, its play history is also deleted

**Indexes**:
```sql
CREATE INDEX idx_play_history_date ON play_history(played_date);
```

---

### Table: `suggestions`

Tracks what Mitch suggested and acceptance rate.

```sql
CREATE TABLE suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    suggested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context TEXT,
    accepted BOOLEAN DEFAULT 0,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE SET NULL
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `game_id`: Reference to suggested game (nullable for generic suggestions)
- `suggested_date`: When the suggestion was made
- `context`: Context of suggestion (e.g., "4 players online")
- `accepted`: Whether the suggestion was accepted (0 or 1)

**Foreign Keys**:
- `game_id` → `games(id)` with `ON DELETE SET NULL`
  - If a game is deleted, suggestions remain but game_id becomes NULL

**Indexes**:
```sql
CREATE INDEX idx_suggestions_date ON suggestions(suggested_date);
```

---

## Python API Usage

### Initialization

```python
from game_tracker import GameTracker

# Default database path (data/mitch.db)
tracker = GameTracker()

# Custom database path
tracker = GameTracker(db_path='custom/path/to/db.db')

# Using config
from config_loader import load_config
config = load_config()
tracker = GameTracker(config=config)
```

### Adding Games

```python
# Add a game
game_id = tracker.add_game(
    name="Phasmophobia",
    min_players=1,
    max_players=4,
    category="co-op",
    tags=["horror", "investigation"]
)

# Returns game_id if successful, None if duplicate
if game_id:
    print(f"Added game with ID: {game_id}")
else:
    print("Game already exists")
```

### Querying Games

```python
# Get all games
all_games = tracker.get_all_games()
for game in all_games:
    print(f"{game['name']} ({game['min_players']}-{game['max_players']} players)")

# Get games for specific player count
games_for_4 = tracker.get_games_for_players(4)
print(f"Found {len(games_for_4)} games for 4 players")

# Find game by name (case-insensitive)
game = tracker.get_game_by_name("phasmophobia")
if game:
    print(f"Found: {game['name']}")
    print(f"Tags: {', '.join(game['tags'])}")

# Get game by ID
game = tracker.get_game_by_id(1)
```

### Recording Play History

```python
# Record a play session
game = tracker.get_game_by_name("Phasmophobia")
if game:
    play_id = tracker.record_play(
        game_id=game['id'],
        player_count=4,
        notes="Great session, everyone survived!"
    )

# Get recent plays (last 7 days by default)
recent_plays = tracker.get_recent_plays(days=7)
for play in recent_plays:
    print(f"{play['game_name']} - {play['played_date']}")
    print(f"  Players: {play['player_count']}")

# Get plays from last 30 days
month_plays = tracker.get_recent_plays(days=30)
```

### Tracking Suggestions

```python
# Record a suggestion
game = tracker.get_game_by_name("Valheim")
suggestion_id = tracker.record_suggestion(
    game_id=game['id'],
    context="5 players online, looking for co-op"
)

# Mark suggestion as accepted (they played the game)
tracker.mark_suggestion_accepted(suggestion_id)

# Get suggestion statistics
stats = tracker.get_suggestion_stats()
print(f"Total suggestions: {stats['total_suggestions']}")
print(f"Acceptance rate: {stats['acceptance_rate']}%")
print(f"Recent (30 days): {stats['recent_suggestions']}")

# Top suggested games
for game in stats['top_suggested_games']:
    print(f"{game['name']}: {game['suggestion_count']} times")
```

### Database Management

```python
# Get overall statistics
stats = tracker.get_stats()
print(f"Total games: {stats['total_games']}")
print(f"Total plays: {stats['total_plays']}")
print(f"Total suggestions: {stats['total_suggestions']}")

# Delete a game (cascades to play_history)
tracker.delete_game(game_id=5)

# Clear entire library (with caution!)
tracker.clear_all_games()  # Deletes everything!

# Close connection (optional, auto-managed)
tracker.close()
```

---

## Script Usage

### Populate Game Library

```bash
# Add all games from scripts/setup_games.py
python3 scripts/setup_games.py populate

# Output:
# Setting up Mitch's game library...
# ✓ Added Phasmophobia (1-4 players, co-op)
# ✓ Added Lethal Company (1-4 players, co-op)
# ...
# ✓ Library setup complete! Added 16 games.
```

### List Games

```bash
# Show current game library
python3 scripts/setup_games.py list

# Output:
# Mitch's Game Library (16 games):
# CO-OP:
#   • Deep Rock Galactic (1-4 players) - shooter, mining, dwarves
#   • Phasmophobia (1-4 players) - horror, investigation, voice-chat
# ...
```

### Database Statistics

```bash
# Show database stats
python3 scripts/setup_games.py stats

# Output:
# Mitch Database Statistics:
# Total Games: 16
# Total Plays: 42
# Total Suggestions: 28
```

### Clear Library

```bash
# Clear all games (with confirmation)
python3 scripts/setup_games.py clear

# Output:
# ⚠️  WARNING: This will delete ALL games, play history, and suggestions!
# Are you sure? Type 'yes' to confirm: yes
# ✓ Library cleared successfully.
```

### Test Database

```bash
# Run comprehensive database tests
python3 scripts/test_database.py

# Output:
# Mitch Database Testing Utility
# [1] Testing Database Initialization
# ✓ Database file created
# ✓ Database tables created
# ...
# ✓ All database tests passed!
```

---

## Query Examples

### Direct SQL Queries

If you need custom queries, you can use SQL directly:

```python
import sqlite3

conn = sqlite3.connect('data/mitch.db')
conn.row_factory = sqlite3.Row  # Return dict-like rows
cursor = conn.cursor()

# Custom query: Most played games
cursor.execute("""
    SELECT 
        g.name,
        COUNT(p.id) as play_count
    FROM games g
    LEFT JOIN play_history p ON g.id = p.game_id
    GROUP BY g.id
    ORDER BY play_count DESC
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"{row['name']}: {row['play_count']} plays")

conn.close()
```

### Common Query Patterns

**Games played in last week:**
```python
recent = tracker.get_recent_plays(days=7)
game_names = [play['game_name'] for play in recent]
```

**Games supporting 3-5 players:**
```python
games_3 = set(g['name'] for g in tracker.get_games_for_players(3))
games_4 = set(g['name'] for g in tracker.get_games_for_players(4))
games_5 = set(g['name'] for g in tracker.get_games_for_players(5))
games_3_to_5 = games_3 & games_4 & games_5
```

**Co-op games not played recently:**
```python
all_coop = [g for g in tracker.get_all_games() if g['category'] == 'co-op']
recent_plays = tracker.get_recent_plays(days=14)
recent_game_ids = {play['game_id'] for play in recent_plays}
fresh_coop = [g for g in all_coop if g['id'] not in recent_game_ids]
```

---

## Database Configuration

In `config/config.yaml`:

```yaml
database:
  # Database file path
  path: "data/mitch.db"
  
  # Enable foreign key constraints
  foreign_keys: true
  
  # Journal mode (WAL recommended)
  journal_mode: "WAL"
```

**Journal Modes**:
- `WAL` (Write-Ahead Logging): Best for concurrent access, recommended
- `DELETE`: Default SQLite mode, simpler but slower
- `MEMORY`: Fastest but no durability

**Foreign Keys**:
- Always enabled in GameTracker
- Ensures referential integrity
- Prevents orphaned records

---

## Performance Notes

### Indexes

Three indexes speed up common queries:
1. `idx_games_players` - Fast player count lookups
2. `idx_play_history_date` - Fast recent plays queries
3. `idx_suggestions_date` - Fast suggestion history queries

### WAL Mode

Write-Ahead Logging provides:
- Concurrent reads during writes
- Better performance for write-heavy workloads
- Atomic commits

**Side Effects**:
- Creates `-wal` and `-shm` files (temporary, don't commit these)
- Uses slightly more disk space

### Connection Pooling

GameTracker uses a connection-per-operation model:
- Each method gets a fresh connection
- Connections auto-close via context managers
- Thread-safe (each thread gets own connection)

For high-frequency operations, consider connection pooling:
```python
# Future enhancement possibility
tracker = GameTracker(pool_size=5)
```

---

## Backup and Restore

### Backup Database

```bash
# Simple file copy (stop bot first)
cp data/mitch.db data/mitch.db.backup

# Or use SQLite's backup command
sqlite3 data/mitch.db ".backup data/mitch.db.backup"
```

### Restore Database

```bash
# Replace database file
cp data/mitch.db.backup data/mitch.db

# Restart bot to pick up changes
sudo systemctl restart mitch
```

### Export to JSON

```python
import json
from game_tracker import GameTracker

tracker = GameTracker()

# Export all games
games = tracker.get_all_games()
with open('games_backup.json', 'w') as f:
    json.dump(games, f, indent=2, default=str)

print(f"Exported {len(games)} games")
```

### Import from JSON

```python
import json
from game_tracker import GameTracker

tracker = GameTracker()

with open('games_backup.json', 'r') as f:
    games = json.load(f)

for game in games:
    tracker.add_game(
        name=game['name'],
        min_players=game['min_players'],
        max_players=game['max_players'],
        category=game.get('category'),
        tags=game.get('tags')
    )

print(f"Imported {len(games)} games")
```

---

## Migration Guide

### Adding New Columns

If you need to add columns to tables:

```python
import sqlite3

conn = sqlite3.connect('data/mitch.db')
cursor = conn.cursor()

# Add new column (must have default or allow NULL)
cursor.execute("""
    ALTER TABLE games 
    ADD COLUMN difficulty TEXT DEFAULT 'medium'
""")

conn.commit()
conn.close()
```

### Schema Versioning

For future schema changes, consider versioning:

```python
# Add version table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Track current version
cursor.execute("INSERT INTO schema_version (version) VALUES (1)")
```

---

## Troubleshooting

### Database Locked Error

```
sqlite3.OperationalError: database is locked
```

**Cause**: Multiple processes trying to write simultaneously.

**Solutions**:
1. Use WAL mode (already enabled)
2. Increase timeout: `sqlite3.connect(db, timeout=30)`
3. Ensure connections are properly closed

### Foreign Key Constraint Failed

```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

**Cause**: Trying to reference non-existent game_id.

**Solutions**:
1. Verify game exists before recording plays/suggestions
2. Check for proper cascade settings
3. Ensure foreign keys are enabled

### Tags Not Loading

If tags come back as strings instead of lists:

```python
# Wrong
tags_str = game['tags']  # "[\"horror\", \"co-op\"]"

# Right (GameTracker does this automatically)
tags_list = json.loads(game['tags'])  # ["horror", "co-op"]
```

GameTracker handles JSON parsing automatically, so you should always get lists.

---

## Security Notes

### SQL Injection Prevention

GameTracker uses parameterized queries everywhere:

```python
# SAFE - parameterized
cursor.execute("SELECT * FROM games WHERE name = ?", (name,))

# UNSAFE - string formatting (never do this!)
cursor.execute(f"SELECT * FROM games WHERE name = '{name}'")
```

All GameTracker methods use safe parameterized queries.

### File Permissions

Database file should be readable only by bot user:

```bash
# Set proper permissions (Linux)
chmod 600 data/mitch.db
chown mitch:mitch data/mitch.db
```

### Backup Encryption

For sensitive data, encrypt backups:

```bash
# Encrypt backup
gpg -c data/mitch.db.backup

# Decrypt when needed
gpg -d data/mitch.db.backup.gpg > data/mitch.db
```

---

## Future Enhancements

Potential database improvements for future versions:

### Planned Features
- **User preferences**: Track individual user game preferences
- **Session tracking**: Link multiple plays into sessions
- **Game statistics**: Win/loss tracking for competitive games
- **Friend groups**: Track different friend groups and their game preferences

### Schema Evolution
```sql
-- User preferences table
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    discord_id TEXT UNIQUE NOT NULL,
    favorite_games TEXT,  -- JSON array
    disliked_games TEXT   -- JSON array
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    notes TEXT
);

-- Link plays to sessions
ALTER TABLE play_history ADD COLUMN session_id INTEGER REFERENCES sessions(id);
```

These are ideas for future development!

---

## Related Documentation

- **Setup Guide**: See [QUICKSTART.md](../QUICKSTART.md)
- **API Reference**: See Python docstrings in `src/game_tracker.py`
- **Configuration**: See `config/config.yaml.example`
- **Testing**: See `scripts/test_database.py`

---

**Questions?** Check the main [README.md](../README.md) or open an issue on GitHub.
