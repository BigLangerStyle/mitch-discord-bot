#!/usr/bin/env python3
"""
Mitch Health Check - Verify all systems operational

Returns exit code 0 if healthy, 1 if issues detected.
Useful for monitoring and systemd health checks.

Usage:
    python3 scripts/health_check.py
"""

import sys
import os
import sqlite3
from pathlib import Path
import shutil

def check_ollama():
    """Verify Ollama is running and responsive."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            raise Exception(f"Ollama returned status {response.status_code}")
        
        # Check if phi3:mini is available
        data = response.json()
        models = [model.get('name', '') for model in data.get('models', [])]
        if not any('phi3:mini' in model for model in models):
            raise Exception("phi3:mini model not found")
            
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama (is it running?)")
    except requests.exceptions.Timeout:
        raise Exception("Ollama request timed out")
    except ImportError:
        raise Exception("requests library not installed")
    except Exception as e:
        raise Exception(f"Ollama check failed: {e}")


def check_database():
    """Verify database is accessible and has data."""
    db_path = Path("data/mitch.db")
    
    if not db_path.exists():
        raise Exception("Database file not found (run: python3 scripts/setup_games.py populate)")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check games table exists and has data
        cursor.execute("SELECT COUNT(*) FROM games")
        game_count = cursor.fetchone()[0]
        
        if game_count == 0:
            raise Exception("Game library is empty (run: python3 scripts/setup_games.py populate)")
        
        # Check play_history table exists
        cursor.execute("SELECT COUNT(*) FROM play_history")
        
        # Check suggestions table exists
        cursor.execute("SELECT COUNT(*) FROM suggestions")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        raise Exception(f"Database error: {e}")
    except Exception as e:
        raise Exception(f"Database check failed: {e}")


def check_config():
    """Verify config file exists and is valid."""
    config_path = Path("config/config.yaml")
    
    if not config_path.exists():
        raise Exception("config.yaml not found (copy from config.yaml.example)")
    
    try:
        import yaml
    except ImportError:
        raise Exception("PyYAML not installed")
    
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['discord', 'logging', 'ollama', 'suggestions']
        missing = [s for s in required_sections if s not in config]
        
        if missing:
            raise Exception(f"Config missing sections: {', '.join(missing)}")
        
        # Check Discord token is configured
        token = config.get('discord', {}).get('token', '')
        if not token or token == 'YOUR_DISCORD_BOT_TOKEN_HERE':
            raise Exception("Discord token not configured")
        
    except yaml.YAMLError as e:
        raise Exception(f"Config YAML syntax error: {e}")
    except Exception as e:
        raise Exception(f"Config check failed: {e}")


def check_disk_space():
    """Verify sufficient disk space for logs and database."""
    try:
        # Check data directory
        data_dir = Path("data")
        if not data_dir.exists():
            data_dir.mkdir(parents=True)
        
        # Check available space (need at least 100MB)
        stat = shutil.disk_usage(data_dir)
        free_mb = stat.free / (1024 * 1024)
        
        if free_mb < 100:
            raise Exception(f"Low disk space: {free_mb:.0f}MB free (need 100MB+)")
            
    except Exception as e:
        raise Exception(f"Disk space check failed: {e}")


def check_log_files():
    """Verify log files are being written."""
    log_path = Path("data/mitch.log")
    
    # Log file might not exist on fresh install - that's okay
    if not log_path.exists():
        # Just verify we can create it
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            log_path.touch()
            return  # Success
        except Exception as e:
            raise Exception(f"Cannot create log file: {e}")
    
    # If it exists, verify it's writable
    try:
        if not os.access(log_path, os.W_OK):
            raise Exception("Log file not writable")
    except Exception as e:
        raise Exception(f"Log file check failed: {e}")


def main():
    """Run all health checks and report status."""
    checks = [
        ("Ollama", check_ollama),
        ("Database", check_database),
        ("Config", check_config),
        ("Disk Space", check_disk_space),
        ("Logs", check_log_files)
    ]
    
    print("=" * 50)
    print("Mitch Health Check")
    print("=" * 50)
    print()
    
    all_passed = True
    for name, check_func in checks:
        try:
            check_func()
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False
    
    print()
    print("=" * 50)
    
    if all_passed:
        print("✓ All systems healthy")
        print("=" * 50)
        print()
        sys.exit(0)
    else:
        print("✗ Some checks failed")
        print("=" * 50)
        print()
        print("Fix the issues above and try again.")
        print("Need help? Check README.md or QUICKSTART.md")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
