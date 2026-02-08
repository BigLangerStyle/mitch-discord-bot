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
    """Test that Python version is 3.9 or higher."""
    version = sys.version_info
    passed = version >= (3, 9)
    
    if passed:
        print_test(
            f"Python version {version.major}.{version.minor}.{version.micro}",
            True
        )
    else:
        print_test(
            "Python version check",
            False,
            f"Found {version.major}.{version.minor}, need 3.9+"
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
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check required keys
        required_keys = ['discord', 'logging']
        missing = [key for key in required_keys if key not in config]
        
        if missing:
            print_test(
                "Config file structure",
                False,
                f"Missing keys: {', '.join(missing)}"
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
            
    except Exception as e:
        print_test(
            "Discord token check",
            False,
            f"Error reading config: {e}"
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
    required_packages = {
        'discord': 'discord.py',
        'yaml': 'PyYAML',
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(name)
    
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
    print("=" * 50)
    print("Mitch Discord Bot - Component Tests")
    print("=" * 50)
    print()
    
    # Run all tests
    test_python_version()
    test_required_directories()
    test_dependencies()
    test_config_file()
    test_discord_token()
    test_logger_setup()
    test_bot_imports()
    
    # Print summary
    print()
    print("=" * 50)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print("=" * 50)
    
    if tests_failed == 0:
        print()
        print("✓ All checks passed! Mitch is ready to run.")
        print()
        print("Next steps:")
        print("  1. Run the bot: ./run.sh")
        print("  2. Test in Discord: @Mitch hey")
        print()
        return 0
    else:
        print()
        print("✗ Some checks failed. Fix the issues above and try again.")
        print()
        print("Need help? Check QUICKSTART.md or README.md")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
