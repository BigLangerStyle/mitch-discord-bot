#!/bin/bash
#
# Mitch Discord Bot - Startup Script
# Works on both Linux and Windows (Git Bash)
#

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Mitch Discord Bot...${NC}"

# Check if config exists
if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}ERROR: config/config.yaml not found${NC}"
    echo -e "${YELLOW}Please copy config/config.yaml.example to config/config.yaml and configure it${NC}"
    echo ""
    echo "  cp config/config.yaml.example config/config.yaml"
    echo "  nano config/config.yaml  # or use your preferred editor"
    echo ""
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found (venv/ or .venv/)${NC}"
    echo -e "${YELLOW}Consider creating one: python3 -m venv venv${NC}"
fi

# Check if discord.py is installed
if ! python3 -c "import discord" 2>/dev/null; then
    echo -e "${RED}ERROR: discord.py not installed${NC}"
    echo -e "${YELLOW}Install dependencies: pip install -r requirements.txt${NC}"
    exit 1
fi

# Run the bot
echo -e "${GREEN}Launching bot...${NC}"
echo ""
python3 src/bot.py

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}Bot exited with code $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi
