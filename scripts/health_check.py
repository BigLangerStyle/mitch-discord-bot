#!/usr/bin/env python3
"""
Mitch Health Check - Verify all systems operational

Returns exit code 0 if healthy, 1 if issues detected.
Useful for monitoring and systemd health checks.
"""

import sys
import os
from pathlib import Path
import urllib.request
import json


def check_ollama():
    """Verify Ollama is running and responsive."""
    try:
        # Try to connect to Ollama API
        req = urllib.request.Request(
            "http://localhost:11434/api/tags",
            method="GET"
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                raise Exception(f"Ollama returned status {response.status}")
            
        return True
    except Exception as e:
        raise Exception(f"Ollama check failed: {e}")


def check_database():
    """Verify database is accessible and has data."""
    try:
        db_path = Path("data/mitch.db")
        
        if not db_path.exists():
            raise Exception("Database file not found (run setup_games.py)")
        
        # Try to open and query the database
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if games table exists and has data
        cursor.execute("SELECT COUNT(*) FROM games")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        if count == 0:
            raise Exception("Database is empty (run setup_games.py populate)")
        
        return True
    except Exception as e:
        raise Exception(f"Database check failed: {e}")


def check_config():
    """Verify config file exists and is valid."""
    try:
        config_path = Path("config/config.yaml")
        
        if not config_path.exists():
            raise Exception("config.yaml not found")
        
        # Try to load config
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check critical sections exist
        if 'discord' not in config:
            raise Exception("Missing 'discord' section in config")
        
        if 'token' not in config['discord']:
            raise Exception("Missing Discord token in config")
        
        token = config['discord']['token']
        if not token or token == 'YOUR_DISCORD_BOT_TOKEN_HERE':
            raise Exception("Discord token not configured")
        
        return True
    except Exception as e:
        raise Exception(f"Config check failed: {e}")


def check_disk_space():
    """Verify sufficient disk space for logs and database."""
    try:
        import shutil
        
        # Check disk space in data directory
        data_path = Path("data")
        if not data_path.exists():
            data_path.mkdir(parents=True)
        
        stat = shutil.disk_usage(data_path)
        free_mb = stat.free / (1024 * 1024)
        
        if free_mb < 100:
            raise Exception(f"Low disk space: {free_mb:.1f}MB free (need 100MB)")
        
        return True
    except Exception as e:
        raise Exception(f"Disk space check failed: {e}")


def check_log_files():
    """Verify log files are writable."""
    try:
        log_path = Path("data/mitch.log")
        
        # If log doesn't exist, that's fine (will be created on first run)
        if log_path.exists():
            # Check if it's writable
            if not os.access(log_path, os.W_OK):
                raise Exception("Log file is not writable")
        else:
            # Check if data directory is writable
            data_path = Path("data")
            if data_path.exists() and not os.access(data_path, os.W_OK):
                raise Exception("Data directory is not writable")
        
        return True
    except Exception as e:
        raise Exception(f"Log files check failed: {e}")


def main():
    """Run all health checks and report status."""
    print("=" * 50)
    print("Mitch Health Check")
    print("=" * 50)
    
    checks = [
        ("Ollama", check_ollama),
        ("Database", check_database),
        ("Config", check_config),
        ("Disk Space", check_disk_space),
        ("Logs", check_log_files)
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            check_func()
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("✓ All systems healthy")
        print("=" * 50)
        print("Mitch is ready to run!")
        sys.exit(0)
    else:
        print("✗ Some checks failed")
        print("=" * 50)
        print("Fix the issues above and try again.")
        print("Need help? Check README.md or QUICKSTART.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
