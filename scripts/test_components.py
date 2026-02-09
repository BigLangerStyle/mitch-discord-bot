#!/usr/bin/env python3
"""
Mitch Discord Bot - Component Test Script

Tests core components to verify installation and configuration.
Run this before deploying to catch common issues early.

Usage:
    python scripts/test_components.py
"""

import sys
import os
from pathlib import Path
import time

# Test results tracking
tests_passed = 0
tests_failed = 0


def print_test(name, passed, message=""):
    """Print test result with formatting."""
    global tests_passed, tests_failed
    
    if passed:
        print(f"✓ {name}")
        tests_passed += 1
    else:
        print(f"✗ {name}")
        if message:
            print(f"  → {message}")
        tests_failed += 1


def test_python_version():
    """Test that Python version is 3.8 or higher."""
    version = sys.version_info
    passed = version >= (3, 8)
    
    if passed:
        print_test(
            f"Python version {version.major}.{version.minor}.{version.micro}",
            True
        )
    else:
        print_test(
            "Python version check",
            False,
            f"Found {version.major}.{version.minor}, need 3.8+"
        )


def test_config_file():
    """Test that config file exists and loads."""
    config_path = Path("config/config.yaml")
    
    if not config_path.exists():
        print_test(
            "Config file exists",
            False,
            "File not found: config/config.yaml (copy from config.yaml.example)"
        )
        return
    
    try:
        import yaml
    except ImportError:
        print_test(
            "Config file check",
            False,
            "PyYAML not installed (run: pip install -r requirements.txt)"
        )
        return
    
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check required keys
        required_keys = ['discord', 'logging', 'ollama', 'suggestions']
        missing = [key for key in required_keys if key not in config]
        
        if missing:
            print_test(
                "Config file structure",
                False,
                f"Missing sections: {', '.join(missing)}"
            )
        else:
            print_test("Config file exists and loads", True)
            
    except yaml.YAMLError as e:
        print_test(
            "Config file syntax",
            False,
            f"YAML syntax error: {e}"
        )
    except Exception as e:
        print_test(
            "Config file loading",
            False,
            f"Unexpected error: {e}"
        )


def test_discord_token():
    """Test that Discord token is configured (basic validation)."""
    try:
        import yaml
    except ImportError:
        print_test(
            "Discord token check",
            False,
            "PyYAML not installed (run: pip install -r requirements.txt)"
        )
        return
    
    try:
        with open("config/config.yaml") as f:
            config = yaml.safe_load(f)
        
        token = config.get('discord', {}).get('token', '')
        
        # Check if token exists and isn't placeholder
        if not token or token == 'YOUR_DISCORD_BOT_TOKEN_HERE':
            print_test(
                "Discord token configured",
                False,
                "Token not set in config/config.yaml"
            )
        elif len(token) < 50:
            print_test(
                "Discord token format",
                False,
                "Token seems too short (Discord tokens are ~70 chars)"
            )
        else:
            print_test("Discord token configured", True)
            
    except FileNotFoundError:
        print_test(
            "Discord token check",
            False,
            "config/config.yaml not found"
        )
    except Exception as e:
        print_test(
            "Discord token check",
            False,
            f"Error reading config: {e}"
        )


def test_ollama_connection():
    """Test Ollama is running and responsive."""
    try:
        import requests
    except ImportError:
        print_test(
            "Ollama connection",
            False,
            "requests library not installed (run: pip install -r requirements.txt)"
        )
        return
    
    try:
        # Try health check with short timeout
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code != 200:
            print_test(
                "Ollama connection",
                False,
                f"Ollama returned status {response.status_code}"
            )
            return
        
        # Check if phi3:mini is available
        data = response.json()
        models = [model.get('name', '') for model in data.get('models', [])]
        
        if not any('phi3:mini' in model for model in models):
            print_test(
                "Ollama phi3:mini model",
                False,
                "Model not found (run: ollama pull phi3:mini)"
            )
        else:
            print_test("Ollama connection working", True)
            
    except requests.exceptions.ConnectionError:
        print_test(
            "Ollama connection",
            False,
            "Cannot connect to Ollama (is it running? Check: systemctl status ollama)"
        )
    except requests.exceptions.Timeout:
        print_test(
            "Ollama connection",
            False,
            "Ollama request timed out (is Ollama overloaded?)"
        )
    except Exception as e:
        print_test(
            "Ollama connection",
            False,
            f"Unexpected error: {e}"
        )


def test_database_operations():
    """Test database operations comprehensively."""
    try:
        import sqlite3
    except ImportError:
        print_test(
            "Database operations",
            False,
            "sqlite3 not available (should be built into Python)"
        )
        return
    
    db_path = Path("data/mitch.db")
    
    if not db_path.exists():
        print_test(
            "Database operations",
            False,
            "Database not found (run: python3 scripts/setup_games.py populate)"
        )
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['games', 'play_history', 'suggestions']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print_test(
                "Database schema",
                False,
                f"Missing tables: {', '.join(missing_tables)}"
            )
            conn.close()
            return
        
        # Check games table has data
        cursor.execute("SELECT COUNT(*) FROM games")
        game_count = cursor.fetchone()[0]
        
        if game_count == 0:
            print_test(
                "Database operations",
                False,
                "Game library is empty (run: python3 scripts/setup_games.py populate)"
            )
            conn.close()
            return
        
        # Check indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Should have indexes on player counts and timestamps
        if len(indexes) == 0:
            print_test(
                "Database indexes",
                False,
                "No indexes found (performance may suffer)"
            )
        
        conn.close()
        print_test(f"Database operations working ({game_count} games)", True)
        
    except sqlite3.OperationalError as e:
        print_test(
            "Database operations",
            False,
            f"Database error: {e}"
        )
    except Exception as e:
        print_test(
            "Database operations",
            False,
            f"Unexpected error: {e}"
        )


def test_suggestion_engine():
    """Test suggestion engine components can be imported."""
    try:
        # Add src to path temporarily
        sys.path.insert(0, str(Path('src').absolute()))
        
        # Just verify we can import the modules
        from game_tracker import GameTracker
        from suggestion_engine import SuggestionEngine
        
        # Verify GameTracker can be instantiated
        tracker = GameTracker()
        
        # If we got here, imports work
        # Full integration testing happens in scripts/test_suggestions.py
        print_test("Suggestion engine modules importable", True)
            
    except ImportError as e:
        print_test(
            "Suggestion engine",
            False,
            f"Cannot import suggestion modules: {e}"
        )
    except Exception as e:
        print_test(
            "Suggestion engine",
            False,
            f"Unexpected error: {e}"
        )
    finally:
        # Remove from path
        if str(Path('src').absolute()) in sys.path:
            sys.path.remove(str(Path('src').absolute()))


def test_performance_baseline():
    """Establish performance baselines."""
    try:
        import requests
    except ImportError:
        print_test(
            "Performance baseline",
            False,
            "requests library not installed"
        )
        return
    
    try:
        # Time a simple AI request
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": "Say hi",
                "stream": False
            },
            timeout=30
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            if elapsed < 10:
                print_test(f"AI response time ({elapsed:.1f}s)", True)
            elif elapsed < 20:
                print_test(
                    f"AI response time ({elapsed:.1f}s - slower than ideal)",
                    True
                )
            else:
                print_test(
                    "AI response time",
                    False,
                    f"{elapsed:.1f}s (very slow - check system load)"
                )
        else:
            print_test(
                "AI response time",
                False,
                f"Request failed with status {response.status_code}"
            )
            
    except requests.exceptions.Timeout:
        print_test(
            "AI response time",
            False,
            "Request timed out after 30s (Ollama overloaded or slow hardware?)"
        )
    except Exception as e:
        print_test(
            "AI response time",
            False,
            f"Unexpected error: {e}"
        )


def test_logger_setup():
    """Test that logger can create log files."""
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Test log file creation
        test_log = data_dir / "test.log"
        test_log.write_text("test")
        test_log.unlink()  # Clean up
        
        print_test("Logger can create log files", True)
        
    except PermissionError:
        print_test(
            "Logger file creation",
            False,
            "Permission denied creating log files in data/"
        )
    except Exception as e:
        print_test(
            "Logger file creation",
            False,
            f"Error: {e}"
        )


def test_required_directories():
    """Test that required directories exist."""
    required = ['src', 'config', 'scripts']
    missing = [d for d in required if not Path(d).exists()]
    
    if missing:
        print_test(
            "Required directories",
            False,
            f"Missing: {', '.join(missing)}"
        )
    else:
        print_test("Required directories exist", True)


def test_dependencies():
    """Test that required Python packages are installed."""
    missing = []
    
    # Test discord.py
    try:
        import discord
    except ImportError:
        missing.append('discord.py')
    
    # Test PyYAML
    try:
        import yaml
    except ImportError:
        missing.append('PyYAML')
    
    # Test requests
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    if missing:
        print_test(
            "Python dependencies",
            False,
            f"Missing: {', '.join(missing)} (run: pip install -r requirements.txt)"
        )
    else:
        print_test("Python dependencies installed", True)


def test_bot_imports():
    """Test that bot modules can be imported."""
    try:
        # Add src to path temporarily
        sys.path.insert(0, str(Path('src').absolute()))
        
        # Try importing bot modules
        import config_loader
        import logger
        import game_tracker
        import suggestion_engine  # Correct module name
        import ollama_client
        import personality
        
        print_test("Bot modules can be imported", True)
        
    except ImportError as e:
        print_test(
            "Bot module imports",
            False,
            f"Import error: {e}"
        )
    except Exception as e:
        print_test(
            "Bot module imports",
            False,
            f"Unexpected error: {e}"
        )
    finally:
        # Remove from path
        if str(Path('src').absolute()) in sys.path:
            sys.path.remove(str(Path('src').absolute()))


def main():
    """Run all component tests."""
    print("=" * 60)
    print("Mitch Discord Bot - Comprehensive Component Tests")
    print("=" * 60)
    print()
    
    # Run all tests
    print("Basic System Checks:")
    test_python_version()
    test_required_directories()
    test_dependencies()
    test_logger_setup()
    
    print()
    print("Configuration Checks:")
    test_config_file()
    test_discord_token()
    
    print()
    print("Core Components:")
    test_bot_imports()
    test_ollama_connection()
    test_database_operations()
    test_suggestion_engine()
    
    print()
    print("Performance Check:")
    test_performance_baseline()
    
    # Print summary
    print()
    print("=" * 60)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print("=" * 60)
    
    if tests_failed == 0:
        print()
        print("✓ All checks passed! Mitch is ready for production.")
        print()
        print("Next steps:")
        print("  1. Run health check: python3 scripts/health_check.py")
        print("  2. Deploy as service: sudo systemctl start mitch")
        print("  3. Monitor logs: sudo journalctl -u mitch -f")
        print("  4. Test in Discord: @Mitch what should we play?")
        print()
        return 0
    else:
        print()
        print("✗ Some checks failed. Fix the issues above and try again.")
        print()
        print("Common fixes:")
        print("  - Missing config: cp config/config.yaml.example config/config.yaml")
        print("  - Missing dependencies: pip install -r requirements.txt")
        print("  - Ollama not running: systemctl start ollama")
        print("  - Empty database: python3 scripts/setup_games.py populate")
        print()
        print("Need more help? Check QUICKSTART.md or README.md")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
