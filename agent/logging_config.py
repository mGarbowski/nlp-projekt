"""Logging configuration for the agent package."""

import os
import sys

from loguru import logger


def configure_logging() -> None:
    """Configure a single Loguru console sink.

    Reconfiguration is safe because we remove default handlers first.
    """

    logger.remove()
    logger.add(
        sys.stdout,
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
