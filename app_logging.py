"""
Application-wide logging helper for AI Skin Specialist.

This module provides a logger that is safe for an internship project:
- It is easy to use from any pipeline module.
- It does NOT log API keys, patient transcripts, or other sensitive data.
- It centralizes the logging format so the app is easier to debug.

No new dependencies are introduced. The logging level and format are configurable,
but the defaults are chosen for clarity during development.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

_app_logger: Optional[logging.Logger] = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a logger for the AI Skin Specialist application.

    Args:
        name: Use __name__ from the calling module (e.g. "brain_of_the_doctor_groq")
              to get a logger that identifies the component. Pass None for the shared
              app logger.

    Returns:
        A logging.Logger instance.
    """
    if name is None:
        global _app_logger
        if _app_logger is None:
            _app_logger = logging.getLogger("ai_skin_specialist")
        return _app_logger
    return logging.getLogger(name)


def configure_logging(
    level: int = logging.INFO,
    fmt: Optional[str] = None,
) -> None:
    """
    Configure application logging if it has not already been configured.

    Call this once at startup, before any analysis runs. It attaches a single
    console handler to the shared app logger and sets a readable format.

    This function deliberately does NOT print or log any secrets, API keys,
    patient transcripts, or similar sensitive values. Individual pipeline
    functions are still responsible for avoiding those in their logs.
    """
    global _app_logger
    if _app_logger is None:
        _app_logger = logging.getLogger("ai_skin_specialist")
    if _app_logger.handlers:
        return

    if fmt is None:
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    _app_logger.setLevel(level)
    _app_logger.addHandler(handler)
    _app_logger.propagate = False
