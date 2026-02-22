"""
Logging Configuration Module
Centralized logging setup for all modules
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from collections import deque


class BoundedMemoryHandler(logging.Handler):
    """
    Custom handler that stores logs in a bounded circular buffer.
    Prevents unbounded memory growth from logging.
    
    Args:
        capacity: Maximum number of records to keep (default 1000)
    """
    def __init__(self, capacity: int = 1000):
        super().__init__()
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
    
    def emit(self, record):
        """Add log record to bounded buffer."""
        try:
            msg = self.format(record)
            self.buffer.append(msg)
        except Exception:
            self.handleError(record)
    
    def get_records(self, last_n: int = None) -> list:
        """
        Get log records from buffer.
        
        Args:
            last_n: Return last N records (None = all)
            
        Returns:
            List of log messages
        """
        records = list(self.buffer)
        if last_n is not None:
            return records[-last_n:]
        return records


def setup_logging(log_dir: str = "logs", level=logging.INFO, memory_buffer_capacity: int = 1000):
    """
    Setup logging for the entire application with bounded memory buffer.
    
    Args:
        log_dir: Directory to store log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        memory_buffer_capacity: Max records to keep in memory buffer (prevents unbounded growth)
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
    
    # Bounded memory handler
    memory_handler = BoundedMemoryHandler(capacity=memory_buffer_capacity)
    memory_handler.setLevel(level)
    
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
    logger.addHandler(memory_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name):
    """Get logger for a specific module"""
    return logging.getLogger(f"deployment_monitor.{name}")
