"""
Logging setup for Mitch Discord Bot.

Provides rotating file logs and console output with proper formatting.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


# Global logger registry to avoid duplicate handlers
_loggers = {}


def setup_logging(
    log_file: str = 'data/mitch.log',
    log_level: str = 'INFO',
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    console_output: bool = True
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to log file (created if doesn't exist)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Max size of log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to also log to console
        
    Note:
        Creates the log file's parent directory if it doesn't exist.
        Safe to call multiple times - will only configure once.
    """
    # Ensure data directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert log level string to constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Only configure if not already configured
    if root_logger.handlers:
        return
    
    root_logger.setLevel(numeric_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        fmt='%(levelname)-8s | %(name)-15s | %(message)s'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Reduce noise from discord.py and other verbose libraries
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    logging.getLogger('discord.gateway').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info('Bot started')
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


def configure_from_config(config) -> None:
    """
    Configure logging from a Config object.
    
    Args:
        config: Config object with logging settings
        
    Example:
        >>> from config_loader import load_config
        >>> from logger import configure_from_config
        >>> config = load_config()
        >>> configure_from_config(config)
    """
    setup_logging(
        log_file=config.get('logging.file', 'data/mitch.log'),
        log_level=config.get('logging.level', 'INFO'),
        max_bytes=config.get('logging.max_size', 10 * 1024 * 1024),
        backup_count=config.get('logging.backup_count', 5),
        console_output=True
    )


if __name__ == '__main__':
    # Test logging setup
    setup_logging(log_level='DEBUG')
    
    logger = get_logger('test')
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    logger.critical('Critical message')
    
    print("\n✓ Logging test complete")
    print("  Check data/mitch.log for output")
