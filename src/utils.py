"""
Utility functions for Mitch Discord Bot.

Error handling, validation, and helper functions to prevent crashes.
"""

import sys
import logging
from pathlib import Path
from typing import Callable, Any, Optional, TypeVar


T = TypeVar('T')


def safe_execute(
    func: Callable[..., T],
    fallback: T,
    logger: Optional[logging.Logger] = None,
    error_msg: str = "Operation failed",
    *args,
    **kwargs
) -> T:
    """
    Execute a function with error handling and fallback.
    
    Args:
        func: Function to execute
        fallback: Value to return if function fails
        logger: Logger for error messages (optional)
        error_msg: Custom error message
        *args: Arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result of func or fallback if func raises an exception
        
    Example:
        >>> def risky_operation():
        ...     return 1 / 0
        >>> result = safe_execute(risky_operation, fallback=0, logger=logger)
        >>> print(result)  # 0
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if logger:
            logger.error(f"{error_msg}: {type(e).__name__}: {e}")
        return fallback


def validate_environment() -> tuple[bool, list[str]]:
    """
    Validate that the environment is suitable for running the bot.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
        
    Example:
        >>> valid, issues = validate_environment()
        >>> if not valid:
        ...     for issue in issues:
        ...         print(f"✗ {issue}")
    """
    issues = []
    
    # Check Python version (3.9+)
    py_version = sys.version_info
    if py_version < (3, 9):
        issues.append(
            f"Python 3.9+ required (found {py_version.major}.{py_version.minor})"
        )
    
    # Check required directories exist or can be created
    required_dirs = ['data', 'config']
    project_root = Path(__file__).parent.parent
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create directory '{dir_name}': {e}")
    
    # Check config file exists
    config_file = project_root / 'config' / 'config.yaml'
    example_file = project_root / 'config' / 'config.yaml.example'
    
    if not config_file.exists() and not example_file.exists():
        issues.append("No config file found (need config.yaml or config.yaml.example)")
    
    return (len(issues) == 0, issues)


def ensure_directory(path: str | Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        True if directory exists or was created, False on error
        
    Example:
        >>> ensure_directory('data/backups')
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False


def truncate_message(message: str, max_length: int = 2000) -> str:
    """
    Truncate a message to fit Discord's 2000 character limit.
    
    Args:
        message: Message to truncate
        max_length: Maximum length (default 2000 for Discord)
        
    Returns:
        Truncated message with ellipsis if needed
        
    Example:
        >>> long_msg = "x" * 3000
        >>> short = truncate_message(long_msg)
        >>> len(short) <= 2000
        True
    """
    if len(message) <= max_length:
        return message
    
    # Leave room for ellipsis
    truncated = message[:max_length - 4]
    return truncated + "..."


def format_file_size(bytes: int) -> str:
    """
    Format bytes as human-readable size.
    
    Args:
        bytes: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
        
    Example:
        >>> format_file_size(1536000)
        '1.5 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} PB"


def get_project_version() -> str:
    """
    Get the current project version.
    
    Returns:
        Version string (e.g., "1.0.0")
        
    Note:
        Currently returns a hardcoded version. In the future,
        this could read from a VERSION file or git tags.
    """
    return "0.2.0-dev"


if __name__ == '__main__':
    # Test utilities
    print("Testing environment validation...")
    valid, issues = validate_environment()
    
    if valid:
        print("✓ Environment validation passed")
    else:
        print("✗ Environment validation failed:")
        for issue in issues:
            print(f"  - {issue}")
    
    print("\nTesting safe_execute...")
    
    def failing_func():
        return 1 / 0
    
    result = safe_execute(failing_func, fallback=-1)
    print(f"  safe_execute with error: {result}")
    
    def working_func(x, y):
        return x + y
    
    result = safe_execute(working_func, fallback=0, error_msg="Addition failed", x=5, y=3)
    print(f"  safe_execute without error: {result}")
    
    print("\nTesting truncate_message...")
    long_msg = "x" * 3000
    short_msg = truncate_message(long_msg)
    print(f"  Truncated 3000 chars to {len(short_msg)} chars")
    
    print("\nTesting format_file_size...")
    print(f"  1536000 bytes = {format_file_size(1536000)}")
    print(f"  5242880 bytes = {format_file_size(5242880)}")
    
    print("\n✓ All utility tests complete")
