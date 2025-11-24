"""Logging utilities for A²-Bench."""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Set up logging configuration.

    Args:
        level: Logging level
        log_file: Optional log file path
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
