"""
Unit tests for configuration loader.

Tests config loading, validation, and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_loader import load_config, Config, ConfigError


class TestConfig:
    """Test cases for the Config class."""
    
    def test_dict_access(self):
        """Test dictionary-style access to config."""
        config = Config({'discord': {'token': 'test-token'}})
        assert config['discord']['token'] == 'test-token'
    
    def test_dot_notation_access(self):
        """Test dot notation access to nested config values."""
        config = Config({
            'discord': {
                'token': 'test-token',
                'guild_id': 12345
            }
        })
        assert config.get('discord.token') == 'test-token'
        assert config.get('discord.guild_id') == 12345
    
    def test_missing_key_returns_default(self):
        """Test that missing keys return default value."""
        config = Config({'discord': {'token': 'test'}})
        assert config.get('missing.key', 'default') == 'default'
        assert config.get('discord.missing', None) is None
    
    def test_contains_operator(self):
        """Test 'in' operator support."""
        config = Config({'discord': {'token': 'test'}})
        assert 'discord' in config
        assert 'missing' not in config
    
    def test_to_dict(self):
        """Test conversion back to dictionary."""
        original = {'discord': {'token': 'test'}}
        config = Config(original)
        assert config.to_dict() == original


class TestLoadConfig:
    """Test cases for config loading."""
    
    def create_temp_config(self, content: dict) -> str:
        """Helper to create a temporary config file."""
        fd, path = tempfile.mkstemp(suffix='.yaml')
        with os.fdopen(fd, 'w') as f:
            yaml.dump(content, f)
        return path
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        valid_config = {
            'discord': {
                'token': 'real-token-here',
                'guild_id': 123456789
            },
            'ollama': {
                'host': 'http://localhost:11434',
                'model': 'phi3:mini'
            },
            'database': {
                'path': 'data/mitch.db'
            },
            'logging': {
                'level': 'INFO',
                'file': 'data/mitch.log'
            }
        }
        
        config_path = self.create_temp_config(valid_config)
        try:
            config = load_config(config_path)
            assert config.get('discord.token') == 'real-token-here'
            assert config.get('discord.guild_id') == 123456789
            assert config.get('ollama.model') == 'phi3:mini'
        finally:
            os.unlink(config_path)
    
    def test_missing_config_file(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(ConfigError, match="Config file not found"):
            load_config('/nonexistent/config.yaml')
    
    def test_invalid_yaml(self):
        """Test error when YAML is malformed."""
        fd, path = tempfile.mkstemp(suffix='.yaml')
        with os.fdopen(fd, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        try:
            with pytest.raises(ConfigError, match="Invalid YAML"):
                load_config(path)
        finally:
            os.unlink(path)
    
    def test_empty_config_file(self):
        """Test error when config file is empty."""
        fd, path = tempfile.mkstemp(suffix='.yaml')
        os.close(fd)
        
        try:
            with pytest.raises(ConfigError, match="empty"):
                load_config(path)
        finally:
            os.unlink(path)
    
    def test_missing_required_fields(self):
        """Test validation catches missing required fields."""
        incomplete_config = {
            'discord': {
                'token': 'test-token'
                # Missing guild_id
            },
            'ollama': {
                'host': 'http://localhost:11434'
                # Missing model
            }
        }
        
        config_path = self.create_temp_config(incomplete_config)
        try:
            with pytest.raises(ConfigError, match="Missing required"):
                load_config(config_path)
        finally:
            os.unlink(config_path)
    
    def test_placeholder_token_rejected(self):
        """Test that placeholder token values are rejected."""
        placeholder_config = {
            'discord': {
                'token': 'your-bot-token-here',  # Placeholder
                'guild_id': 123456789
            },
            'ollama': {
                'host': 'http://localhost:11434',
                'model': 'phi3:mini'
            },
            'database': {
                'path': 'data/mitch.db'
            },
            'logging': {
                'level': 'INFO',
                'file': 'data/mitch.log'
            }
        }
        
        config_path = self.create_temp_config(placeholder_config)
        try:
            with pytest.raises(ConfigError, match="placeholder value"):
                load_config(config_path)
        finally:
            os.unlink(config_path)
    
    def test_placeholder_guild_id_rejected(self):
        """Test that placeholder guild ID values are rejected."""
        placeholder_config = {
            'discord': {
                'token': 'real-token',
                'guild_id': 'your-guild-id-here'  # Placeholder string
            },
            'ollama': {
                'host': 'http://localhost:11434',
                'model': 'phi3:mini'
            },
            'database': {
                'path': 'data/mitch.db'
            },
            'logging': {
                'level': 'INFO',
                'file': 'data/mitch.log'
            }
        }
        
        config_path = self.create_temp_config(placeholder_config)
        try:
            with pytest.raises(ConfigError, match="placeholder value"):
                load_config(config_path)
        finally:
            os.unlink(config_path)
    
    def test_invalid_log_level(self):
        """Test that invalid log levels are rejected."""
        invalid_config = {
            'discord': {
                'token': 'real-token',
                'guild_id': 123456789
            },
            'ollama': {
                'host': 'http://localhost:11434',
                'model': 'phi3:mini'
            },
            'database': {
                'path': 'data/mitch.db'
            },
            'logging': {
                'level': 'INVALID_LEVEL',  # Invalid
                'file': 'data/mitch.log'
            }
        }
        
        config_path = self.create_temp_config(invalid_config)
        try:
            with pytest.raises(ConfigError, match="logging.level must be one of"):
                load_config(config_path)
        finally:
            os.unlink(config_path)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
