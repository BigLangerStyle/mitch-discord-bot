"""
Configuration loader for Mitch Discord Bot.

Loads YAML configuration with validation and fallback support.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """Configuration container with dot notation access."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get config value using dot notation.
        
        Args:
            key: Config key in dot notation (e.g., 'discord.token')
            default: Default value if key not found
            
        Returns:
            Config value or default
            
        Example:
            >>> config.get('discord.token')
            'your-token-here'
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access: config['discord']"""
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator."""
        return key in self._config
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the underlying dictionary."""
        return self._config.copy()


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, uses default paths.
        
    Returns:
        Config object with loaded configuration
        
    Raises:
        ConfigError: If config is missing or invalid
        
    Note:
        Falls back to config.yaml.example for development if config.yaml
        doesn't exist.
    """
    # Determine config file path
    if config_path is None:
        # Look for config.yaml in config/ directory
        project_root = Path(__file__).parent.parent
        primary_path = project_root / 'config' / 'config.yaml'
        fallback_path = project_root / 'config' / 'config.yaml.example'
        
        if primary_path.exists():
            config_path = str(primary_path)
        elif fallback_path.exists():
            config_path = str(fallback_path)
            print(f"⚠️  Using example config: {fallback_path}")
            print("   Copy config.yaml.example to config.yaml and customize it.")
        else:
            raise ConfigError(
                "No config file found. Expected config/config.yaml or "
                "config/config.yaml.example"
            )
    
    # Load YAML
    try:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in config file: {e}")
    
    if config_dict is None:
        raise ConfigError(f"Config file is empty: {config_path}")
    
    # Validate required fields
    config = Config(config_dict)
    _validate_config(config)
    
    return config


def _validate_config(config: Config) -> None:
    """
    Validate that required config fields are present.
    
    Args:
        config: Config object to validate
        
    Raises:
        ConfigError: If required fields are missing or invalid
    """
    required_fields = [
        ('discord.token', 'Discord bot token'),
        ('discord.guild_id', 'Discord guild (server) ID'),
        ('ollama.host', 'Ollama API host'),
        ('ollama.model', 'Ollama model name'),
        ('database.path', 'Database file path'),
        ('logging.level', 'Logging level'),
        ('logging.file', 'Log file path'),
    ]
    
    missing = []
    for field, description in required_fields:
        value = config.get(field)
        if value is None or value == '':
            missing.append(f"{field} ({description})")
    
    if missing:
        raise ConfigError(
            "Missing required configuration fields:\n" +
            "\n".join(f"  - {field}" for field in missing)
        )
    
    # Validate specific fields
    discord_token = config.get('discord.token')
    if discord_token == 'your-bot-token-here':
        raise ConfigError(
            "discord.token is still set to placeholder value. "
            "Get your token from https://discord.com/developers/applications"
        )
    
    guild_id = config.get('discord.guild_id')
    if guild_id == 'your-guild-id-here' or guild_id == 0:
        raise ConfigError(
            "discord.guild_id is still set to placeholder value. "
            "Enable Developer Mode in Discord, right-click your server, "
            "and select 'Copy Server ID'"
        )
    
    # Validate logging level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    log_level = config.get('logging.level', '').upper()
    if log_level not in valid_levels:
        raise ConfigError(
            f"logging.level must be one of: {', '.join(valid_levels)}"
        )


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


if __name__ == '__main__':
    # Test config loading
    try:
        config = load_config()
        print("✓ Config loaded successfully")
        print(f"  Discord guild ID: {config.get('discord.guild_id')}")
        print(f"  Ollama model: {config.get('ollama.model')}")
        print(f"  Log level: {config.get('logging.level')}")
    except ConfigError as e:
        print(f"✗ Config error: {e}")
        sys.exit(1)
