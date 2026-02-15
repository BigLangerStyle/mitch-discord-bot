# Troubleshooting Guide

**Version:** 1.2.0  
**Last Updated:** February 2026

This guide covers common issues you might encounter with Mitch and how to solve them.

---

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Bot Connection Issues](#bot-connection-issues)
- [Ollama / AI Issues](#ollama--ai-issues)
- [Database Issues](#database-issues)
- [Game Suggestion Issues](#game-suggestion-issues)
- [Performance Issues](#performance-issues)
- [Deployment Issues](#deployment-issues)
- [Log Analysis](#log-analysis)
- [Getting Help](#getting-help)

---

## Quick Diagnostics

**Run this first to check overall health:**

```bash
# Test all components
python3 scripts/test_components.py
```

**Expected output when healthy:**
```
✓ Config loaded successfully
✓ Database connection working
✓ Ollama connection working
✓ All imports successful
```

**One-line status check (if running as service):**
```bash
sudo systemctl status mitch && echo "--- Recent Logs ---" && sudo journalctl -u mitch -n 20 --no-pager
```

---

## Bot Connection Issues

### Issue: Bot Not Responding to @Mentions

**Symptoms:**
- Bot shows as online in Discord
- No response when you @mention it
- No errors in logs

**Possible Causes & Solutions:**

#### 1. **Privileged Gateway Intents Not Enabled**

The bot needs three privileged intents to function properly.

**How to fix:**
1. Go to https://discord.com/developers/applications
2. Select your application
3. Go to "Bot" section
4. Scroll to "Privileged Gateway Intents"
5. Enable all three:
   - ✅ **Message Content Intent** (required to read messages)
   - ✅ **Server Members Intent** (required to see who's in the server)
   - ✅ **Presence Intent** (required to see who's online/offline)
6. Click "Save Changes"
7. Restart bot: `sudo systemctl restart mitch`

**Why each intent is needed:**
- **Message Content Intent**: Bot can't read message text without this
- **Server Members Intent**: Bot can't count players without this
- **Presence Intent**: Bot can't tell who's online without this (will show "0 online")

**How to verify:**
```bash
# Check bot logs for mention detection
sudo journalctl -u mitch -n 50 | grep "Received message"
```

---

#### 2. **Bot Token Incorrect**

**How to verify:**
```bash
# Check if bot connects
sudo journalctl -u mitch -n 20 | grep "Logged in"
```

**If you see "Improper token" error:**
1. Go to https://discord.com/developers/applications
2. Select your application → Bot
3. Click "Reset Token"
4. Copy new token
5. Update `config/config.yaml`:
   ```yaml
   discord:
     token: "NEW_TOKEN_HERE"
   ```
6. Restart bot: `sudo systemctl restart mitch`

---

#### 3. **Bot Lacks Permissions**

**Required permissions:**
- Read Messages
- Send Messages
- Read Message History

**How to verify:**
1. Right-click the bot in Discord
2. Check role permissions
3. Ensure bot role has permissions above

**If missing permissions:**
1. Server Settings → Roles
2. Find bot's role
3. Enable required permissions
4. Or reinvite bot with correct permissions:
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=67584&scope=bot
   ```

---

#### 4. **Rate Limited**

If rate limiting is enabled in config, the bot might be ignoring you.

**Check config:**
```yaml
rate_limiting:
  enabled: true  # ← If true, bot rate limits users
  cooldown_seconds: 5
```

**How to test:**
1. Wait 10 seconds
2. Try @mentioning again
3. Check logs for "rate limited" messages

**To disable:**
```yaml
rate_limiting:
  enabled: false
```

---

### Issue: Bot Goes Offline After Starting

**Symptoms:**
- Bot connects briefly
- Shows online, then goes offline
- Logs show disconnect errors

**Possible Causes:**

#### 1. **Invalid Guild ID**

**How to diagnose:**
```bash
sudo journalctl -u mitch -n 50 | grep -i "guild"
```

**If you see errors about guild not found:**
1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click your server icon
3. Click "Copy Server ID"
4. Update config.yaml:
   ```yaml
   discord:
     guild_id: 1234567890123456789  # Your actual guild ID
   ```
5. Restart bot

---

#### 2. **Bot Kicked from Server**

**Check:**
1. Is bot still in your Discord server?
2. Check server member list

**If bot was removed:**
1. Reinvite using OAuth URL (see Discord Developer Portal)

---

## Ollama / AI Issues

### Issue: Ollama Connection Failed

**Symptoms:**
- Bot responds, but with fallback messages like "not sure what's good right now"
- Logs show "Failed to connect to Ollama"
- No AI-generated responses

**Diagnose:**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Expected: {"version":"0.1.x"}
# If fails: Ollama is not running
```

**Solutions:**

#### Start Ollama

**If installed via binary:**
```bash
ollama serve
```

**If installed via snap:**
```bash
sudo snap start ollama
```

**If installed as systemd service:**
```bash
sudo systemctl start ollama
sudo systemctl status ollama
```

---

#### Verify Ollama is Accessible

```bash
# Test API endpoint
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"phi3:mini","prompt":"test","stream":false}'
```

**Expected:** JSON response with model output  
**If fails:** Check Ollama logs, verify port 11434 is open

---

### Issue: Model Not Found

**Symptoms:**
- Ollama is running
- But bot logs show "model 'phi3:mini' not found"

**Solution:**

```bash
# Pull the model
ollama pull phi3:mini

# Verify it's downloaded
ollama list
```

**Expected output:**
```
NAME            ID              SIZE
phi3:mini       abc123def       2.3GB
```

**If model download fails:**
- Check internet connection
- Check disk space: `df -h`
- Try different model: `ollama pull llama2`

---

### Issue: Ollama Timeouts

**Symptoms:**
- Bot responds sometimes
- Long delays (30-60+ seconds)
- Logs show "Ollama request timed out"

**Normal Behavior:**
- First request after idle: 10-30 seconds (cold start)
- Subsequent requests: 3-10 seconds
- MediaServer (i3-3225): 5-20 seconds is normal

**When to Worry:**
- Consistent 60+ second timeouts
- Timeouts on every request

**Solutions:**

#### Increase Timeout

Edit `config/config.yaml`:
```yaml
ollama:
  timeout: 120  # Increase from 60 to 120 seconds
```

Restart bot: `sudo systemctl restart mitch`

---

#### Check System Resources

```bash
# Check CPU usage
top

# Check memory
free -h

# Check if Ollama is using resources
ps aux | grep ollama
```

**If Ollama is using 100% CPU:**
- Normal during inference
- Should drop after response generated

**If system is swapping:**
```bash
free -h
# Check "Swap" line - if used is high, you're out of RAM
```

**Solution:** Reduce concurrent AI requests in config:
```yaml
performance:
  max_concurrent_ai_requests: 1  # Reduce from 2 to 1
```

---

#### Test Ollama Directly

```bash
# Time how long Ollama takes
time ollama run phi3:mini "what should we play?"
```

**Expected:** 3-20 seconds depending on hardware  
**If 60+ seconds:** Ollama is slow, increase bot timeout

---

### Issue: AI Responses Are Weird

**Symptoms:**
- Responses don't match Mitch's personality
- Too formal, robotic, or overly enthusiastic
- Lots of emojis or corporate language

**Causes:**

#### 1. **Polishing Not Working**

**Check personality.py is being used:**
```bash
sudo journalctl -u mitch -n 50 | grep "Polishing"
```

**If no "Polishing" logs:** personality.py might not be loaded correctly

**Test manually:**
```bash
python3 scripts/test_ai.py
# Try various prompts, check if responses are polished
```

---

#### 2. **Wrong Model**

**Check which model is being used:**
```bash
grep "model:" config/config.yaml
```

**If not phi3:mini:**
- Different models have different personalities
- phi3:mini is tuned for casual conversation
- llama2 might be more formal

**Solution:** Switch to phi3:mini in config

---

#### 3. **Temperature Too Low/High**

```yaml
ollama:
  temperature: 0.8  # Recommended
```

**Too low (< 0.5):** Repetitive, boring responses  
**Too high (> 1.0):** Random, chaotic responses

---

## Database Issues

### Issue: Database Is Locked

**Symptoms:**
- Errors in logs: "database is locked"
- Suggestion requests fail
- Play history not recording

**Causes:**

#### 1. **Multiple Processes Accessing Database**

**Check:**
```bash
# See what's accessing the database
lsof ~/git/mitch-discord-bot/data/mitch.db
```

**If multiple processes:**
- Kill old bot instances
- Restart bot cleanly

---

#### 2. **WAL Mode Not Enabled**

**Verify:**
```bash
sqlite3 ~/git/mitch-discord-bot/data/mitch.db "PRAGMA journal_mode;"
```

**Expected:** `wal`  
**If not WAL:**

```bash
sqlite3 ~/git/mitch-discord-bot/data/mitch.db "PRAGMA journal_mode=WAL;"
```

Or set in config:
```yaml
database:
  journal_mode: "WAL"
```

---

### Issue: Database Corrupted

**Symptoms:**
- "database disk image is malformed"
- Query errors
- Bot can't start

**Diagnose:**
```bash
sqlite3 ~/git/mitch-discord-bot/data/mitch.db "PRAGMA integrity_check;"
```

**Expected:** `ok`  
**If not ok:** Database is corrupted

**Solution (if no backup):**
```bash
# Backup corrupted database
cp data/mitch.db data/mitch.db.corrupted

# Try to recover
sqlite3 data/mitch.db ".recover" | sqlite3 data/mitch.db.recovered

# If recovery works, replace
mv data/mitch.db.recovered data/mitch.db

# Repopulate game library
python3 scripts/setup_games.py populate
```

**Solution (if you have backup):**
```bash
# Restore from backup
cp data/mitch.db.backup data/mitch.db
```

**Prevention:** Backup database regularly:
```bash
# Add to cron
0 2 * * * cp ~/git/mitch-discord-bot/data/mitch.db ~/backups/mitch-$(date +\%Y\%m\%d).db
```

---

### Issue: Game Library Empty

**Symptoms:**
- Bot says "your game library is empty"
- No suggestions work
- `setup_games.py list` shows 0 games

**Solution:**

```bash
# Populate with sample games
python3 scripts/setup_games.py populate
```

**Expected output:**
```
✓ Added Phasmophobia (1-4 players, co-op)
✓ Added Valheim (1-10 players, co-op)
...
✓ Library setup complete! Added 16 games.
```

**If populate fails:**
```bash
# Check database exists
ls -la data/mitch.db

# Check database permissions
ls -la data/

# If permissions wrong:
chmod 644 data/mitch.db
chmod 755 data/
```

---

## Game Suggestion Issues

### Issue: Bot Says "Not Sure What's Good Right Now"

**Symptoms:**
- Bot responds to suggestion requests
- But always says "not sure" or generic fallback

**Diagnose Step-by-Step:**

#### 1. **Check Game Library**

```bash
python3 scripts/setup_games.py list
```

**If empty:** Run `python3 scripts/setup_games.py populate`

---

#### 2. **Check Player Count Matching**

```bash
# Test suggestions with different player counts
python3 scripts/test_suggestions.py
```

Try: 2 players, 4 players, 8 players

**If no games match:**
- Library might only have games for specific player counts
- Add more games or adjust player count filters

---

#### 3. **Check Cooldown Settings**

```yaml
suggestions:
  cooldown_hours: 48  # ← Might be too strict
```

**If all games were played recently:**
```bash
# Check recent plays
sqlite3 data/mitch.db \
  "SELECT g.name, datetime(p.played_date) 
   FROM play_history p 
   JOIN games g ON p.game_id = g.id 
   ORDER BY p.played_date DESC 
   LIMIT 10;"
```

**Solutions:**
- Reduce cooldown: `cooldown_hours: 24`
- Or manually clear history: `python3 scripts/setup_games.py clear-history`

---

#### 4. **Check AI is Working**

```bash
# Test AI directly
python3 scripts/test_ai.py
```

**If AI fails:** See [Ollama Issues](#ollama--ai-issues)

---

### Issue: Suggestions Seem Random

**Symptoms:**
- Bot suggests games you just played
- Ignores player count
- Same game suggested repeatedly

**Diagnose:**

#### 1. **Verify Play History Recording**

```bash
# After playing a game, manually record it
python3 -c "from src.game_tracker import GameTracker; t = GameTracker(); t.record_play('Deep Rock Galactic')"

# Check it was recorded
sqlite3 data/mitch.db \
  "SELECT g.name, datetime(p.played_date) 
   FROM play_history p 
   JOIN games g ON p.game_id = g.id 
   ORDER BY p.played_date DESC 
   LIMIT 5;"
```

**If not recording:** Database write issue, check permissions

---

#### 2. **Check Cooldown Logic**

```bash
# Run test with debug output
python3 -c "
from src.suggestion_engine import SuggestionEngine
from src.config_loader import load_config

config = load_config('config/config.yaml')
engine = SuggestionEngine(config)

# This should show filtered games
result = engine.get_suggestion(player_count=4)
print(result)
"
```

---

#### 3. **Verify Player Count Detection**

```bash
# Check logs for player count
sudo journalctl -u mitch -n 50 | grep "Estimated player count"
```

**If player count is always 1:**
- Bot might not be counting online members correctly
- Check guild_id in config matches your server

---

## Performance Issues

### Issue: High Memory Usage

**Symptoms:**
- RAM usage spikes during AI generation
- System becomes slow
- Out of memory errors

**Expected Behavior:**
- **Baseline:** ~50MB
- **During AI inference:** ~600MB spike
- **After response:** Returns to baseline

**When to Worry:**
- Sustained 90%+ RAM usage
- Memory doesn't return to baseline
- Bot becomes unresponsive

**Diagnose:**

```bash
# Check bot memory usage
ps aux | grep python | grep mitch

# Watch in real-time
watch -n 1 'ps aux | grep python | grep mitch'
```

**Solutions:**

#### Reduce Concurrent Requests

```yaml
performance:
  max_concurrent_ai_requests: 1  # Down from 2
```

#### Reduce Context Messages

```yaml
conversation:
  context_messages: 3  # Down from 5
```

#### Reduce Max Tokens

```yaml
ollama:
  max_tokens: 200  # Down from 300
```

#### Add Swap (if needed)

```bash
# Check current swap
free -h

# Add 2GB swap file (if you have none)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### Issue: Slow Response Times

**Symptoms:**
- 30+ second delays
- Typing indicator shows for a long time

**Normal Response Times (MediaServer):**
- Casual chat: 3-10 seconds
- Suggestions: 5-20 seconds
- Cold start: 10-30 seconds

**If 30+ seconds consistently:**

#### Check System Load

```bash
# Check CPU usage
top

# Check I/O wait
iostat -x 1 5
```

**High CPU:** Normal during AI inference  
**High I/O wait:** Disk might be slow or failing

#### Check Ollama Performance

```bash
# Time Ollama directly
time ollama run phi3:mini "test prompt"
```

**If Ollama is slow:** Hardware limitation, consider:
- Smaller model (phi3:mini is already smallest)
- Increase timeout in config
- Use faster hardware for Ollama

---

## Deployment Issues

### Issue: Systemd Service Won't Start

**Symptoms:**
```bash
sudo systemctl start mitch
# Failed to start mitch.service
```

**Diagnose:**

```bash
# Check service status
sudo systemctl status mitch

# Check recent logs
sudo journalctl -u mitch -n 50
```

**Common Causes:**

#### 1. **Wrong Path in Service File**

Check `/etc/systemd/system/mitch.service`:
```ini
WorkingDirectory=/home/your-user/git/mitch-discord-bot
ExecStart=/home/your-user/git/mitch-discord-bot/venv/bin/python3 src/bot.py
```

**Verify paths exist:**
```bash
ls -la /home/your-user/git/mitch-discord-bot
ls -la /home/your-user/git/mitch-discord-bot/venv/bin/python3
```

---

#### 2. **Wrong User**

Service file should match your user:
```ini
User=your-username
Group=your-groupname
```

**Verify:**
```bash
id  # Shows your username and group
```

---

#### 3. **Permission Issues**

```bash
# Check if user can access files
sudo -u your-username ls ~/git/mitch-discord-bot

# Check config file permissions
ls -la ~/git/mitch-discord-bot/config/config.yaml
```

**If permission denied:**
```bash
chmod 644 config/config.yaml
chmod 755 data/
```

---

#### 4. **Config File Missing**

```bash
# Check config exists
ls -la config/config.yaml

# If missing, copy example
cp config/config.yaml.example config/config.yaml
nano config/config.yaml  # Add your token
```

---

### Issue: Service Starts But Bot Doesn't Work

**Check logs:**
```bash
sudo journalctl -u mitch -f
```

**Look for:**
- Import errors → Missing dependencies, reinstall requirements
- Config errors → Invalid config.yaml
- Connection errors → Discord token or Ollama issues

---

## Log Analysis

### Viewing Logs

**If running as systemd service:**
```bash
# Last 50 lines
sudo journalctl -u mitch -n 50

# Follow in real-time
sudo journalctl -u mitch -f

# Specific time range
sudo journalctl -u mitch --since "1 hour ago"

# Today's logs
sudo journalctl -u mitch --since today
```

**If running manually:**
```bash
# View log file
tail -f data/mitch.log

# Search for errors
grep ERROR data/mitch.log
```

---

### Common Log Patterns

**Looking for errors:**
```bash
sudo journalctl -u mitch | grep -i error
```

**Looking for suggestion requests:**
```bash
sudo journalctl -u mitch | grep "suggestion request"
```

**Looking for AI timeouts:**
```bash
sudo journalctl -u mitch | grep -i timeout
```

**Looking for rate limiting:**
```bash
sudo journalctl -u mitch | grep "rate limited"
```

**Checking Ollama connection:**
```bash
sudo journalctl -u mitch | grep -i ollama
```

---

### Log Levels

```
DEBUG   - Detailed diagnostic info (enable in config for troubleshooting)
INFO    - Normal operation events
WARNING - Something unusual but not broken
ERROR   - Something failed but bot continues
CRITICAL- Something failed and bot might crash
```

**To enable debug logging:**
```yaml
logging:
  level: "DEBUG"
```

Restart bot after changing log level.

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide** - Your issue might be here
2. **Check logs** - Error messages are helpful
3. **Test components** - Run `scripts/test_components.py`
4. **Try simplest case** - Does basic @mention work?

### Information to Provide

When asking for help, include:

1. **What you were trying to do**
   - Example: "Trying to get a game suggestion"

2. **What happened**
   - Example: "Bot said 'not sure what's good right now'"

3. **Relevant logs**
   ```bash
   sudo journalctl -u mitch -n 100 > mitch-logs.txt
   ```

4. **Config (without token!)**
   ```bash
   # Copy config and remove token before sharing
   cp config/config.yaml config-debug.yaml
   sed -i 's/token: .*/token: REDACTED/' config-debug.yaml
   ```

5. **Component test results**
   ```bash
   python3 scripts/test_components.py > test-results.txt
   ```

6. **System info**
   ```bash
   python3 --version
   ollama --version
   uname -a
   free -h
   ```

---

## Still Stuck?

If this guide doesn't solve your issue:

1. **Check GitHub Issues** (if project is open-sourced)
2. **Review recent changes** - Did you change config recently?
3. **Try a clean restart:**
   ```bash
   sudo systemctl stop mitch
   # Wait 10 seconds
   sudo systemctl start mitch
   sudo journalctl -u mitch -f
   ```

4. **Test in isolation:**
   ```bash
   # Stop service
   sudo systemctl stop mitch
   
   # Run manually to see errors directly
   cd ~/git/mitch-discord-bot
   source venv/bin/activate
   python3 src/bot.py
   ```

---

**Good luck!** Most issues are quick fixes - usually config, permissions, or Ollama not running.

---

**Related Documentation:**
- [Architecture Overview](ARCHITECTURE.md) - How components work
- [Configuration Reference](CONFIGURATION.md) - All config options
- [Deployment Guide](DEPLOYMENT.md) - Production setup
- [Database Documentation](DATABASE.md) - Database operations
