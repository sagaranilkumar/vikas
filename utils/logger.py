"""
Logger module for the Feedback Processing System.
Provides a centralized logging configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Define log formats
CONSOLE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
FILE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logger(name: str = None, log_level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """
    Set up and configure a logger with both console and file handlers.
    
    Args:
        name: Name of the logger (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (optional)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name or 'root')
    logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    
    # Prevent adding handlers multiple times in case of multiple calls
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    console_formatter = logging.Formatter(CONSOLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        try:
            # Ensure the log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
            file_formatter = logging.Formatter(FILE_FORMAT)
            file_handler.setFormatter(file_formatter)
            
            # Add file handler to logger
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {str(e)}")
    
    return logger

# Create a default logger instance
logger = setup_logger(__name__)

if __name__ == "__main__":
    # Test the logger
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
