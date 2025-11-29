"""
Logging configuration for Telnyx Transcribe.

Provides consistent, formatted logging across the application.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_style: str = "detailed",
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional file path for log output.
        format_style: Format style ('detailed', 'simple', or 'json').
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Define format based on style
    formats = {
        "detailed": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        "simple": "%(levelname)s: %(message)s",
        "json": '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    }
    
    log_format = formats.get(format_style, formats["detailed"])
    
    # Configure root logger
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers,
        force=True,
    )
    
    # Set third-party loggers to WARNING to reduce noise
    for logger_name in ("urllib3", "httpx", "openai", "telnyx"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__).
        
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
