"""
Logging Configuration for Aeris

This module provides structured logging with both console and file output.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

import colorlog
from config import AppConfig


def setup_logger(
    name: str,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.

    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, uses config default)

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Set logging level
    level = log_level or AppConfig.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))

    # =========================================================================
    # Console Handler (with colors)
    # =========================================================================
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Color formatter
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # =========================================================================
    # File Handler (rotating)
    # =========================================================================
    log_file_path = log_file or AppConfig.LOG_FILE

    # Ensure log directory exists
    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=AppConfig.LOG_MAX_BYTES,
        backupCount=AppConfig.LOG_BACKUP_COUNT,
    )
    file_handler.setLevel(logging.DEBUG)

    # File formatter (no colors)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return setup_logger(name)


# ==============================================================================
# Create default logger for the package
# ==============================================================================
default_logger = get_logger("aeris")


# ==============================================================================
# Convenience functions
# ==============================================================================

def log_api_request(logger: logging.Logger, method: str, url: str, params: dict = None):
    """Log API request details"""
    params_str = f" | Params: {params}" if params else ""
    logger.debug(f"API Request: {method} {url}{params_str}")


def log_api_response(logger: logging.Logger, status_code: int, response_time: float):
    """Log API response details"""
    logger.debug(f"API Response: Status {status_code} | Time: {response_time:.2f}s")


def log_database_operation(logger: logging.Logger, operation: str, table: str, count: int = None):
    """Log database operation"""
    count_str = f" | Records: {count}" if count is not None else ""
    logger.debug(f"Database: {operation} | Table: {table}{count_str}")


def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None):
    """Log error with additional context"""
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    logger.error(error_msg, exc_info=True)
