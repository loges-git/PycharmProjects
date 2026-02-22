"""
Logging Configuration Module
Centralized logging setup for all modules
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logging(log_dir: str = "logs", level=logging.INFO):
    """
    Setup logging for the entire application.
    
    Args:
        log_dir: Directory to store log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("deployment_monitor")
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with rotation
    log_file = log_path / f"deployment_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name):
    """Get logger for a specific module"""
    return logging.getLogger(f"deployment_monitor.{name}")
