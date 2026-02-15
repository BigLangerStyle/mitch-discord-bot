# Mitch Discord Bot - Quick Start Guide

Get Mitch up and running in your Discord server in under 10 minutes.

---

## Prerequisites

Before you begin, make sure you have:

- **Python 3.9 or higher** installed
- **Git** for cloning the repository
- **A Discord account** with permission to add bots to your server
- **A Discord bot token** (we'll get this in the next section)

---

## Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name (e.g., "Mitch")
3. Go to the **"Bot"** tab on the left
4. Click **"Add Bot"** and confirm
5. Under the bot's username, click **"Reset Token"** and copy the token (save it somewhere safe!)
6. Scroll down to **"Privileged Gateway Intents"** and enable:
   - ✅ **Server Members Intent**
   - ✅ **Message Content Intent**
   - ✅ **Presence Intent**
7. Click **"Save Changes"**

### Get Your Server (Guild) ID

1. Open Discord and enable Developer Mode:
   - Settings → Advanced → Enable "Developer Mode"
2. Right-click your server icon and select **"Copy Server ID"**
3. Save this ID for later

### Invite the Bot to Your Server

1. In the Developer Portal, go to **OAuth2 → URL Generator**
2. Select these scopes:
   - ✅ `bot`
3. Select these bot permissions:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Read Message History
4. Copy the generated URL at the bottom
5. Open it in your browser and add the bot to your server

---

## Step 2: Install Mitch

### Clone the Repository

```bash
git clone https://github.com/yourusername/mitch-discord-bot.git
cd mitch-discord-bot
```

### Create a Virtual Environment (Recommended)

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3: Configure the Bot

### Copy the Example Config

```bash
cp config/config.yaml.example config/config.yaml
```

### Edit the Config File

Open `config/config.yaml` in your favorite text editor:

```bash
nano config/config.yaml   # Linux/macOS
notepad config/config.yaml  # Windows
```

Update these values:

```yaml
discord:
  token: "YOUR_BOT_TOKEN_HERE"      # Paste your bot token from Step 1
  guild_id: 1234567890123456789     # Paste your server ID from Step 1
```

**Important:** Never commit `config/config.yaml` to git! It contains your secret bot token.

---

## Step 4: Run the Bot

### Local Testing (All Platforms)

```bash
# Make sure your virtual environment is activated
./run.sh
```

**Windows users:** If `./run.sh` doesn't work, run:
```powershell
python src/bot.py
```

You should see:
```
INFO:bot:Starting Mitch Discord Bot...
INFO:bot:Mitch connected as Mitch#1234
INFO:bot:Ready to help 1 servers
```

### Test in Discord

1. Go to your Discord server
2. In any channel, type: `@Mitch hey`
3. Mitch should respond with something like: `yo what's up?`

**Success!** Mitch is now running. Press `Ctrl+C` to stop the bot.

---

## Step 5: Run as a Service (Linux Only)

For production deployment on a Linux server (like MediaServer), you can run Mitch as a systemd service so it starts automatically.

### Install the Service

```bash
# Copy service file
sudo cp docs/mitch.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable mitch

# Start the service
sudo systemctl start mitch
```

### Check Service Status

```bash
sudo systemctl status mitch
```

You should see `Active: active (running)` in green.

### View Logs

```bash
# Follow logs in real-time
sudo journalctl -u mitch -f

# View recent logs
sudo journalctl -u mitch -n 100
```

### Manage the Service

```bash
# Stop the bot
sudo systemctl stop mitch

# Restart the bot
sudo systemctl restart mitch

# Disable auto-start
sudo systemctl disable mitch
```

---

## Testing Your Installation

Run the component test script to verify everything is set up correctly:

```bash
python scripts/test_components.py
```

This will check:
- ✅ Config file exists and loads
- ✅ Logger creates log files
- ✅ Discord token format is valid
- ✅ Python version is 3.9+
- ✅ Required directories exist

---

## Troubleshooting

### Bot doesn't connect

**Error:** `Failed to login - invalid Discord token`

**Fix:** 
- Double-check your token in `config/config.yaml`
- Make sure there are no extra spaces before/after the token
- Try resetting your token in the Discord Developer Portal

---

### Bot connects but doesn't respond

**Error:** Bot is online but doesn't reply to @mentions

**Fix:**
- Make sure you enabled **Message Content Intent** in the Developer Portal
- Make sure you enabled **Server Members Intent**
- Make sure you enabled **Presence Intent** (required for detecting online members)
- Wait a few minutes after enabling intents (Discord can be slow)
- Restart the bot: `sudo systemctl restart mitch` (or `Ctrl+C` and re-run `./run.sh`)

---

### Import errors or missing modules

**Error:** `ModuleNotFoundError: No module named 'discord'`

**Fix:**
- Make sure your virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.9+)

---

### Permission denied errors (Linux)

**Error:** `PermissionError: [Errno 13] Permission denied: 'data/mitch.log'`

**Fix:**
- Make sure the `data/` directory exists: `mkdir -p data`
- Check file permissions: `ls -la data/`
- If running as a service, make sure the user matches: `sudo systemctl edit mitch` and set `User=yourusername`

---

### Service fails to start (Linux)

**Error:** `systemctl status mitch` shows `failed` or `inactive (dead)`

**Fix:**
1. Check the logs for errors: `sudo journalctl -u mitch -n 50`
2. Make sure the paths in `mitch.service` match your installation
3. Verify the virtual environment exists: `ls -la ~/git/mitch-discord-bot/venv`
4. Test running manually first: `cd ~/git/mitch-discord-bot && ./run.sh`

---

## What's Next?

Mitch is now running with basic mention detection and hardcoded responses. Here's what's coming:

- **v0.3.0:** AI integration with Ollama for natural responses
- **v0.4.0:** Game library and play history tracking
- **v1.0.0:** Full game suggestion capabilities

Want to help build features? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Quick Reference

### Local Development
```bash
source venv/bin/activate  # Activate virtual environment
./run.sh                  # Run the bot
```

### Production (Linux)
```bash
sudo systemctl status mitch    # Check status
sudo systemctl restart mitch   # Restart bot
sudo journalctl -u mitch -f    # View logs
```

### Updating Mitch
```bash
git pull                       # Get latest code
pip install -r requirements.txt  # Update dependencies
sudo systemctl restart mitch   # Restart (if service)
```

---

**Need help?** Check the [README.md](README.md) or open an issue on GitHub.

**Last Updated:** February 2026
