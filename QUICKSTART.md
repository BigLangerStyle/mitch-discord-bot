# Quickstart Guide

**Version:** 0.1.0  
**Status:** Placeholder - Implementation starts in v0.2.0

---

## ⚠️ Note: No Implementation Yet

This repository currently contains only the structure and documentation (v0.1.0). The actual Discord bot code will be added in v0.2.0 and beyond.

For now, this guide serves as a preview of what the setup process will look like.

---

## Future Setup Process (v0.2.0+)

When the implementation is complete, the setup will be roughly:

### 1. Prerequisites
- Python 3.9 or higher
- Discord bot token (from Discord Developer Portal)
- Ollama installed locally
- Linux/macOS/Windows with WSL

### 2. Installation
```bash
# Clone repository
git clone https://github.com/yourusername/mitch-discord-bot.git
cd mitch-discord-bot

# Install dependencies
pip3 install -r requirements.txt

# Copy config template
cp config/config.yaml.example config/config.yaml

# Edit config with your Discord token
nano config/config.yaml
```

### 3. Setup Ollama
```bash
# Pull the phi3:mini model
ollama pull phi3:mini
```

### 4. Run the Bot
```bash
# Quick test
./run.sh

# Or with systemd (production)
sudo cp docs/mitch.service /etc/systemd/system/
sudo systemctl enable mitch
sudo systemctl start mitch
```

### 5. Verify
- @mention the bot in Discord
- Check that it responds
- Add games to the library
- Test suggestions

---

## What's Next?

- **v0.2.0**: Discord bot skeleton will make this actually runnable
- **v0.3.0**: Ollama integration will add AI responses
- **v0.4.0**: Database and game tracking
- **v1.0.0**: Full feature set ready for production

---

## Need Help?

- Check [README.md](README.md) for project overview
- See [CONTRIBUTING.md](CONTRIBUTING.md) to help build features
- Read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for technical details

---

**Come back in v0.2.0+ for actual setup instructions!**
