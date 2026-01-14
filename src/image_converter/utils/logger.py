"""Logging configuration for the image converter."""

import logging
import sys
from typing import Optional


def setup_logger(
    verbose: bool = False,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Configure and return the root logger for the application.
    
    Args:
        verbose: If True, set log level to DEBUG; otherwise INFO.
        log_file: Optional path to write logs to a file.
        
    Returns:
        Configured root logger.
    """
    # Get the package logger
    logger = logging.getLogger("image_converter")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(ColoredFormatter(formatter))
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class ColoredFormatter(logging.Formatter):
    """Formatter that adds ANSI colors to log levels."""
    
    # ANSI color codes
    COLORS = {
        logging.DEBUG: "\033[36m",     # Cyan
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def __init__(self, base_formatter: logging.Formatter):
        """Initialize with a base formatter.
        
        Args:
            base_formatter: The formatter to wrap with colors.
        """
        super().__init__()
        self.base_formatter = base_formatter
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors.
        
        Args:
            record: The log record to format.
            
        Returns:
            Formatted string with ANSI colors.
        """
        # Get the base formatted message
        message = self.base_formatter.format(record)
        
        # Add color based on level
        color = self.COLORS.get(record.levelno, "")
        if color:
            # Color just the level name portion
            return message.replace(
                record.levelname,
                f"{color}{record.levelname}{self.RESET}",
                1,
            )
        return message

