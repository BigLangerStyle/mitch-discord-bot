# Uninstalling Mitch Discord Bot

Guide for completely removing Mitch from your system.

---

## Quick Uninstall

**If you just want to stop the bot:**

```bash
# Stop the service
sudo systemctl stop mitch

# Disable auto-start on boot
sudo systemctl disable mitch

# That's it! Bot is stopped but files remain for later.
```

---

## Complete Removal

**To completely remove everything:**

### 1. Stop and Remove Service

```bash
# Stop the bot
sudo systemctl stop mitch

# Disable auto-start
sudo systemctl disable mitch

# Remove service file
sudo rm /etc/systemd/system/mitch.service

# Reload systemd
sudo systemctl daemon-reload
```

---

### 2. Remove Bot Files

```bash
# Navigate to parent directory
cd ~/git  # Or wherever you installed

# Remove entire project
rm -rf mitch-discord-bot/

# Or if you want to keep the database for backup:
cp mitch-discord-bot/data/mitch.db ~/backups/
rm -rf mitch-discord-bot/
```

---

### 3. Optional: Remove Ollama

**Only do this if you're not using Ollama for anything else!**

```bash
# If installed via install script
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm -rf /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama
sudo rm -rf ~/.ollama

# If installed via snap
sudo snap remove ollama

# If installed via package manager
sudo apt remove ollama  # Debian/Ubuntu
```

---

### 4. Optional: Remove Discord Bot

**In Discord Developer Portal:**

1. Go to https://discord.com/developers/applications
2. Select your Mitch application
3. Click "Delete App" (bottom of General Information)
4. Confirm deletion

**Or just leave it** - it won't do anything without the bot running.

---

### 5. Cleanup (Optional)

**Remove Python virtual environment artifacts:**

```bash
# These were created during installation
# but already removed when you deleted the project directory
# Only needed if you installed elsewhere:

# Remove pip cache (optional)
rm -rf ~/.cache/pip

# Remove any global packages if you installed without venv
# (Not recommended, but just in case)
pip uninstall discord.py PyYAML requests
```

---

## Partial Removal Scenarios

### Keep Bot Files, Just Stop Service

```bash
sudo systemctl stop mitch
sudo systemctl disable mitch
# Files remain in ~/git/mitch-discord-bot/
```

**When to do this:**
- Taking a break from using the bot
- Debugging issues
- Switching to manual running instead of service

---

### Remove Bot But Keep Database

```bash
# Backup database first
cp ~/git/mitch-discord-bot/data/mitch.db ~/mitch-backup.db

# Stop service
sudo systemctl stop mitch
sudo systemctl disable mitch
sudo rm /etc/systemd/system/mitch.service

# Remove bot files
rm -rf ~/git/mitch-discord-bot/

# Database is now in ~/mitch-backup.db
```

**When to do this:**
- Want to preserve game library and play history
- Might reinstall later
- Switching to different server

---

### Remove Service But Keep Manual Running

```bash
# Stop and disable service
sudo systemctl stop mitch
sudo systemctl disable mitch
sudo rm /etc/systemd/system/mitch.service
sudo systemctl daemon-reload

# Bot files remain, run manually:
cd ~/git/mitch-discord-bot
./run.sh
```

**When to do this:**
- Prefer manual control
- Development/testing
- Temporary deployment

---

## Verification

**Verify complete removal:**

```bash
# Check service is gone
systemctl status mitch
# Should show: Unit mitch.service could not be found

# Check files are gone
ls ~/git/mitch-discord-bot
# Should show: No such file or directory

# Check Ollama (if you removed it)
which ollama
# Should show nothing

# Check Discord (bot should be offline)
# Look in your Discord server - bot should appear offline
```

---

## Reinstallation

**If you decide to reinstall later:**

1. **If you kept the database:**
   ```bash
   # Clone fresh repo
   git clone https://github.com/yourusername/mitch-discord-bot.git
   cd mitch-discord-bot
   
   # Copy back database
   mkdir -p data/
   cp ~/mitch-backup.db data/mitch.db
   
   # Continue with normal installation
   ```

2. **Fresh install:**
   - Follow QUICKSTART.md from the beginning
   - Will need to repopulate game library

---

## What Gets Left Behind

Even after complete removal, these might remain:

**Discord Server:**
- Bot remains in server member list (as offline)
- Remove manually: Right-click bot → Kick

**Logs (if journald):**
- Service logs remain in journal
- Clean with: `sudo journalctl --vacuum-time=1d`

**Ollama Models (if kept Ollama):**
- Models remain in ~/.ollama/models/
- Remove with: `ollama rm phi3:mini`

**Python Packages (if installed globally):**
- discord.py, PyYAML remain if not in venv
- Uninstall with: `pip uninstall discord.py PyYAML`

---

## Common Questions

**Q: Will uninstalling delete my game library?**  
A: Yes, if you remove the project directory. Back up `data/mitch.db` first!

**Q: Can I just disable the service without uninstalling?**  
A: Yes! `sudo systemctl disable mitch` stops auto-start but keeps everything else.

**Q: Do I need to remove the Discord bot from Developer Portal?**  
A: No, leaving it there is harmless. The bot just won't be running.

**Q: What if I want to move the bot to a different server?**  
A: Back up `data/mitch.db` and `config/config.yaml`, then install on new server and copy them over.

**Q: Will this remove Plex/Jellyfin/other services on my MediaServer?**  
A: No! This only removes Mitch. Other services are unaffected.

---

## Troubleshooting Uninstall Issues

**Service won't stop:**
```bash
# Force stop
sudo systemctl kill mitch

# Then disable
sudo systemctl disable mitch
```

**Files won't delete (permission denied):**
```bash
# Check who owns the files
ls -la ~/git/mitch-discord-bot/

# If owned by root, use sudo
sudo rm -rf ~/git/mitch-discord-bot/
```

**Service file won't delete:**
```bash
# Use sudo
sudo rm /etc/systemd/system/mitch.service

# Reload systemd
sudo systemctl daemon-reload
```

---

## Need Help?

If you encounter issues during uninstallation:

1. Check logs: `sudo journalctl -u mitch -n 50`
2. Verify what's running: `ps aux | grep mitch`
3. Check for file locks: `lsof | grep mitch`
4. Ask in project issues/discussions

---

**That's it!** Mitch should be completely removed from your system.

Remember to back up your database if you want to keep your game library and play history!
