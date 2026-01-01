import logging
import sys
from typing import Any


def configure_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """
    Configure logging for the application.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        level=level,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
