# Deploying Mitch to Production

Complete guide for deploying Mitch Discord Bot to a production Linux server.

---

## Prerequisites

### System Requirements
- **OS**: Linux (tested on Linux Mint, should work on Ubuntu/Debian)
- **Python**: 3.9 or higher
- **RAM**: 2GB available (bot uses ~150-200MB normally)
- **Disk**: ~100MB for bot + database + logs
- **CPU**: Any modern CPU (tested on i3-3225)

### Required Software
- **Ollama** with phi3:mini model ([Install Guide](https://ollama.ai))
- **Git** for repository management
- **systemd** for service management (standard on most Linux distros)
- **Python venv** module (usually included with Python)

### Discord Setup
- Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
- Bot added to your server with these permissions:
  - Read Messages/View Channels
  - Send Messages
  - Read Message History
- **Privileged Gateway Intents** enabled in Developer Portal:
  - **Message Content Intent**
  - **Server Members Intent**
  - **Presence Intent**

---

## Initial Deployment

### 1. Clone Repository

```bash
# Choose install location (example: ~/git/)
cd ~/git
git clone https://github.com/yourusername/mitch-discord-bot.git
cd mitch-discord-bot
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 --version  # Should be 3.9+
pip list  # Should show discord.py, PyYAML, requests
```

### 3. Install and Configure Ollama

```bash
# Install Ollama (visit https://ollama.ai for your platform)
# On Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama  # Start on boot

# Pull phi3:mini model (this may take a few minutes)
ollama pull phi3:mini

# Verify installation
ollama list  # Should show phi3:mini
curl http://localhost:11434/api/tags  # Should return JSON
```

### 4. Configure Mitch

```bash
# Copy example config
cp config/config.yaml.example config/config.yaml

# Edit configuration
nano config/config.yaml
```

**Required changes in config.yaml:**

```yaml
discord:
  token: "YOUR_ACTUAL_DISCORD_BOT_TOKEN_HERE"  # From Discord Developer Portal
  command_prefix: "!"

logging:
  level: "INFO"  # Use INFO for production
  file: "data/mitch.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5

ollama:
  base_url: "http://localhost:11434"
  model: "phi3:mini"
  temperature: 0.8
  max_tokens: 300
  timeout: 120  # Increase if responses timeout

suggestions:
  cooldown_hours: 48  # Don't suggest games played within 48h
  suggestion_cooldown_minutes: 5  # Limit suggestion frequency
```

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

### 5. Setup Game Library

```bash
# Populate with example games
python3 scripts/setup_games.py populate

# Verify database created
ls -lh data/mitch.db

# View games in library
python3 scripts/setup_games.py list
```

### 6. Run Tests

```bash
# Run comprehensive tests
python3 scripts/test_components.py

# All tests should pass
# If any fail, fix issues before proceeding

# Run health check
python3 scripts/health_check.py

# Should show: ✓ All systems healthy
```

### 7. Test Run (Manual)

```bash
# Start bot manually for testing
./run.sh

# Bot should start and show:
# "Logged in as Mitch#1234"
# "Ready to suggest games!"

# In Discord, test:
# @Mitch hey
# @Mitch what should we play?

# Stop bot: Ctrl+C
```

### 8. Deploy as systemd Service

```bash
# Copy service file
sudo cp docs/mitch.service /etc/systemd/system/

# Edit paths if needed (if you installed elsewhere)
sudo nano /etc/systemd/system/mitch.service
# Update WorkingDirectory and ExecStart paths

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable mitch

# Start service
sudo systemctl start mitch

# Check status
sudo systemctl status mitch
```

**Expected output:**
```
● mitch.service - Mitch Discord Bot
   Loaded: loaded (/etc/systemd/system/mitch.service; enabled)
   Active: active (running) since...
   Memory: 150.0M
```

### 9. Verify Production Deployment

```bash
# Watch logs in real-time
sudo journalctl -u mitch -f

# Should see:
# "Logged in as Mitch#..."
# "Ready to suggest games!"

# Test in Discord
# @Mitch what should we play?

# Check for errors
sudo journalctl -u mitch --since "10 minutes ago" | grep ERROR

# If no errors, deployment successful! ✓
```

---

## Updating Mitch

### Standard Update Process

```bash
# SSH to server
ssh your-server

# Navigate to repo
cd ~/git/mitch-discord-bot

# Pull latest changes
git pull origin main

# Activate venv
source venv/bin/activate

# Update dependencies (if requirements.txt changed)
pip install -r requirements.txt

# Run tests to verify update
python3 scripts/test_components.py

# Restart service
sudo systemctl restart mitch

# Watch logs for issues
sudo journalctl -u mitch -f

# Verify in Discord
# @Mitch hey
```

### Configuration Updates

```bash
# Edit config
nano config/config.yaml

# Make changes, save and exit

# Restart bot to apply changes
sudo systemctl restart mitch

# Verify changes took effect
sudo journalctl -u mitch -f
```

### Game Library Updates

```bash
# Add more games
python3 scripts/setup_games.py populate

# Or manually add games (future feature)
# !addgame "Game Name" min_players max_players
```

---

## Monitoring

### Check Bot Status

```bash
# Service status
sudo systemctl status mitch

# Check if running
ps aux | grep "python3 src/bot.py"

# Quick health check
python3 scripts/health_check.py
```

### View Logs

```bash
# Follow logs in real-time
sudo journalctl -u mitch -f

# Recent logs (last hour)
sudo journalctl -u mitch --since "1 hour ago"

# Today's logs
sudo journalctl -u mitch --since today

# Search for errors
sudo journalctl -u mitch | grep ERROR

# Export logs to file
sudo journalctl -u mitch --since today > mitch-logs.txt
```

### Performance Monitoring

```bash
# Check resource usage
systemctl show mitch --property=CPUUsageNSec
systemctl show mitch --property=MemoryCurrent

# Real-time monitoring
htop -p $(pidof python3)

# Disk usage
du -sh data/
ls -lh data/mitch.db
ls -lh data/mitch.log
```

### Expected Performance (MediaServer Baseline)

- **AI Response Time**: 3-5 seconds average (3-20s range)
- **Database Queries**: < 1ms
- **Memory Usage**: 100-200MB
- **CPU Usage**: 5-10% idle, 20-50% during AI generation

---

## Troubleshooting

### Bot Won't Start

**Check logs:**
```bash
sudo journalctl -u mitch -xe
```

**Common issues:**

1. **Config error:**
   ```bash
   python3 -c "from src.config_loader import load_config; load_config()"
   ```
   Fix: Check config.yaml syntax

2. **Discord token invalid:**
   - Verify token in Discord Developer Portal
   - Copy token exactly (no extra spaces)
   - Regenerate token if needed

3. **Ollama not running:**
   ```bash
   sudo systemctl status ollama
   sudo systemctl start ollama
   ```

4. **Database missing:**
   ```bash
   python3 scripts/setup_games.py populate
   ```

### Slow Responses

1. **Check Ollama performance:**
   ```bash
   python3 scripts/test_ai.py
   ```

2. **Check system load:**
   ```bash
   top
   # Look for high CPU/memory usage from other processes
   ```

3. **Increase timeout in config:**
   ```yaml
   ollama:
     timeout: 180  # Increase from 120 to 180
   ```

4. **Check hardware:**
   - phi3:mini needs ~2GB RAM
   - CPU-only inference is slower than GPU
   - Other services competing for resources

### Database Issues

```bash
# Check database exists
ls -la data/mitch.db

# Check database integrity
sqlite3 data/mitch.db "PRAGMA integrity_check;"

# Check disk space
df -h

# Backup database
cp data/mitch.db data/mitch.db.backup.$(date +%Y%m%d)

# Re-create database if corrupted
rm data/mitch.db
python3 scripts/setup_games.py populate
```

### Ollama Issues

```bash
# Check Ollama status
sudo systemctl status ollama

# Restart Ollama
sudo systemctl restart ollama

# Test directly
ollama run phi3:mini "Say hi"

# Check model list
ollama list

# Re-pull model if needed
ollama pull phi3:mini

# Check Ollama logs
sudo journalctl -u ollama -f
```

### High Memory Usage

```bash
# Check memory
free -h

# Check Mitch's memory
systemctl show mitch --property=MemoryCurrent

# If over 500MB, may indicate memory leak
# Restart bot:
sudo systemctl restart mitch

# If persists, report issue on GitHub
```

### Bot Not Responding in Discord

1. **Check bot is running:**
   ```bash
   sudo systemctl status mitch
   ```

2. **Check logs for errors:**
   ```bash
   sudo journalctl -u mitch -f
   ```

3. **Verify Discord connection:**
   - Look for "Logged in as..." message
   - Look for WebSocket errors

4. **Check Discord permissions:**
   - Bot has Read/Send Messages permissions
   - **Message Content Intent** enabled in Developer Portal
   - **Server Members Intent** enabled in Developer Portal
   - **Presence Intent** enabled in Developer Portal
   - Bot role is above any restrictive roles

5. **Test with @mention:**
   ```
   @Mitch hey
   ```
   Should respond within a few seconds

---

## Backup and Recovery

### Manual Backup

```bash
# Backup everything important
tar -czf mitch-backup-$(date +%Y%m%d).tar.gz \
  config/config.yaml \
  data/mitch.db \
  data/mitch.log

# Store backup safely
mv mitch-backup-*.tar.gz ~/backups/
```

### Automated Backup (Optional)

```bash
# Create backup script
cat > ~/backup-mitch.sh << 'EOF'
#!/bin/bash
cd ~/git/mitch-discord-bot
tar -czf ~/backups/mitch-$(date +%Y%m%d).tar.gz \
  config/config.yaml \
  data/mitch.db
# Keep only last 7 days
find ~/backups/mitch-*.tar.gz -mtime +7 -delete
EOF

chmod +x ~/backup-mitch.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
# 0 2 * * * /home/your-user/backup-mitch.sh
```

### Restore from Backup

```bash
# Stop bot
sudo systemctl stop mitch

# Extract backup
tar -xzf mitch-backup-20260208.tar.gz

# Restart bot
sudo systemctl start mitch

# Verify
sudo journalctl -u mitch -f
```

---

## Performance Tuning

### Ollama Optimization

**If responses are too slow:**

1. **Lower temperature** (faster but less creative):
   ```yaml
   ollama:
     temperature: 0.5  # Lower from 0.8
   ```

2. **Reduce max_tokens** (shorter responses):
   ```yaml
   ollama:
     max_tokens: 200  # Lower from 300
   ```

3. **Increase timeout** (prevent timeouts):
   ```yaml
   ollama:
     timeout: 180  # Increase from 120
   ```

### Database Optimization

**Already optimized with:**
- WAL mode enabled (write-ahead logging)
- Proper indexes on player counts and timestamps
- SQLite is plenty fast for this scale (< 1000 games)

**If database grows large:**
```bash
# Vacuum database (reclaim space)
sqlite3 data/mitch.db "VACUUM;"

# Check size
ls -lh data/mitch.db
```

### Resource Limits

**Adjust in /etc/systemd/system/mitch.service if needed:**

```ini
# Allow more CPU
CPUQuota=50%  # Up from 25%

# Allow more RAM
MemoryMax=3G  # Up from 2G
MemoryHigh=2.5G  # Up from 1.5G
```

**After changes:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart mitch
```

---

## Security

### Discord Token Security

- **Never** commit token to git
- **Never** share token publicly
- Use config file (in .gitignore)
- Rotate token if compromised

### File Permissions

```bash
# Secure config file (only owner can read)
chmod 600 config/config.yaml

# Database readable by bot
chmod 755 data
chmod 644 data/mitch.db

# Logs readable for debugging
chmod 644 data/mitch.log
```

### Network Security

- Ollama listens only on localhost (127.0.0.1)
- No need to expose bot to internet
- Discord connection is outbound only
- No inbound ports needed

### systemd Security Hardening

**Already enabled in mitch.service:**
- `NoNewPrivileges=true` - Can't escalate privileges
- `PrivateTmp=true` - Isolated /tmp directory
- `ProtectSystem=strict` - Read-only system files
- `ProtectHome=true` - Can't access other user home directories
- `ReadWritePaths=...` - Only data/ directory is writable

---

## Common Tasks

### Add Games to Library

```bash
# Using setup script (recommended)
python3 scripts/setup_games.py populate

# View current games
python3 scripts/setup_games.py list

# Clear library (careful!)
python3 scripts/setup_games.py clear
```

### Test AI Responses

```bash
# Interactive AI testing
python3 scripts/test_ai.py

# Prompts Mitch with test scenarios
# See how AI responds
# Useful for tuning personality
```

### View Play History

```bash
sqlite3 data/mitch.db "SELECT * FROM play_history ORDER BY played_at DESC LIMIT 10;"
```

### View Suggestion Statistics

```bash
sqlite3 data/mitch.db "SELECT game_name, COUNT(*) as times_suggested FROM suggestions GROUP BY game_name ORDER BY times_suggested DESC LIMIT 10;"
```

### Reset Database

```bash
# Backup first!
cp data/mitch.db data/mitch.db.backup

# Remove and recreate
rm data/mitch.db
python3 scripts/setup_games.py populate

# Restart bot
sudo systemctl restart mitch
```

---

## Maintenance Schedule

### Daily
- Check bot is running: `systemctl status mitch`
- Watch for error spikes in logs

### Weekly
- Review logs for patterns: `journalctl -u mitch --since "1 week ago" | grep ERROR`
- Check disk space: `df -h`
- Backup database: `cp data/mitch.db backups/`

### Monthly
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Review and prune old logs: `find data/ -name "*.log.*" -mtime +30 -delete`
- Check for Ollama updates: `ollama list`

### As Needed
- Update Mitch: `git pull && systemctl restart mitch`
- Rotate logs if large: `journalctl --vacuum-time=30d`
- Review and optimize game library

---

## Production Checklist

Before declaring production-ready:

- [ ] All tests pass: `python3 scripts/test_components.py`
- [ ] Health check passes: `python3 scripts/health_check.py`
- [ ] Bot runs as service: `systemctl status mitch`
- [ ] Auto-starts on boot: `systemctl is-enabled mitch`
- [ ] Logs to journald: `journalctl -u mitch`
- [ ] Resource limits enforced
- [ ] Config file secured (chmod 600)
- [ ] Discord token configured and working
- [ ] Ollama running and responsive
- [ ] Game library populated
- [ ] Tested in Discord successfully
- [ ] Monitoring in place
- [ ] Backup strategy defined
- [ ] Documentation reviewed

---

## Getting Help

### Resources

- **README.md** - Project overview and features
- **QUICKSTART.md** - Quick setup guide
- **CONTRIBUTING.md** - Development guide
- **GitHub Issues** - Report bugs or request features

### Common Support Requests

1. **"Bot won't start"**
   - Run: `python3 scripts/health_check.py`
   - Check: `sudo journalctl -u mitch -xe`

2. **"Responses are slow"**
   - Normal: 3-20 seconds on MediaServer hardware
   - Check: `python3 scripts/test_ai.py`

3. **"Bot not responding in Discord"**
   - Check: `systemctl status mitch`
   - Verify: Message Content Intent, Server Members Intent, and Presence Intent enabled in Developer Portal

4. **"Need to add games"**
   - Run: `python3 scripts/setup_games.py populate`

---

## Version History

See **[CHANGELOG.md](../CHANGELOG.md)** for detailed version history.

**Current Version:** 1.0.0 - Production Ready

---

**Deployment complete? Head to Discord and try: `@Mitch what should we play?`** 🎮
