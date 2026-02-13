# utils/logger.py

import logging
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "release_ops") -> logging.Logger:
    """Setup application logger"""

    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"

    app_logger = logging.getLogger(name)
    app_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if app_logger.handlers:
        return app_logger

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    app_logger.addHandler(fh)
    app_logger.addHandler(ch)

    return app_logger


# Global logger instance
logger = setup_logger()