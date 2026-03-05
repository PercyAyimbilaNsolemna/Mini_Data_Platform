"""
Centralized logging configuration for the ecommerce data platform.

This module provides a reusable logger with:
    - Console output
    - Rotating file logging
    - Structured formatting
    - Configurable log levels
    - Protection against duplicate handlers

Designed for production-grade data pipelines.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Create and configure a reusable logger instance.

    This function ensures:
        - No duplicate handlers
        - Console + file logging
        - Rotating logs to prevent disk overflow
        - Standardized log format

    Args:
        name (str): Name of the logger (usually __name__).
        log_file (Optional[str]): Custom log filename (optional).

    Returns:
        logging.Logger: Configured logger instance.
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers in interactive / Airflow environments
    if logger.handlers:
        return logger

    # Log level configurable via environment variable
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler
    file_name = log_file or "application.log"
    file_path = LOG_DIR / file_name

    file_handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger