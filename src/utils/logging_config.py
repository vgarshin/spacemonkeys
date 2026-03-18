"""Logging configuration for the project."""

import logging
import sys

from ..config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, DATE_FORMAT

LOG_DIR = LOGS_DIR
LOG_DIR.mkdir(exist_ok=True)

# Convert string log level to logging constant
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
DEFAULT_LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)


def setup_logging(
    log_level: int = DEFAULT_LOG_LEVEL,
    log_to_file: bool = True,
    log_to_console: bool = True,
):
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (e.g., logging.INFO).
        log_to_file: Whether to write logs to file.
        log_to_console: Whether to output logs to console.
    """
    handlers = []

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        handlers.append(console_handler)

    if log_to_file:
        log_file = LOG_DIR / "app.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
    )

    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Shortcut to get a logger with the given name."""
    return logging.getLogger(name)
