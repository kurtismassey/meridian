"""
Logging configuration.
"""

import logging
from pathlib import Path

from rich.logging import RichHandler

PROJECT_ROOT = Path(__file__).parent.parent.parent


class RelativePathFormatter(logging.Formatter):
    """
    Formatter that shows relative paths.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record.
        """
        try:
            record.relpath = Path(record.pathname).relative_to(PROJECT_ROOT)
        except ValueError:
            record.relpath = record.pathname
        return super().format(record)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging.

    Args:
        level: Logging level (default: INFO).
    """
    handler = RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        show_time=True,
        show_path=False,
    )
    handler.setFormatter(
        RelativePathFormatter("%(relpath)s:%(lineno)d | %(funcName)s | %(message)s")
    )

    logging.basicConfig(level=level, handlers=[handler])


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name.

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


setup_logging()
