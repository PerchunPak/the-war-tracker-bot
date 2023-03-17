"""Module for some of our utils."""
import sys
import typing

from loguru import logger

import twtb.logic.shared.logging as logging_config


class Singleton(type):
    """Metaclass to do Singleton pattern."""

    _instances: dict[type, typing.Any] = {}  # type: ignore[misc] # Explicit "Any" is not allowed

    def __call__(cls, *args, **kwargs):
        """Actual logic in this class.

        See https://stackoverflow.com/a/6798042.
        """
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)

            if hasattr(instance, "_setup"):
                instance = instance._setup()
            cls._instances[cls] = instance

        return cls._instances[cls]


def setup_logging() -> None:
    """Setup logging for the addon."""
    # circular imports
    import twtb.config as config_module

    config = config_module.Config()

    logger.remove()
    if config.logging.level < logging_config.LogLevel.WARNING:
        logger.add(
            sys.stdout,
            level=config.logging.level,
            filter=lambda record: record["level"].no < logging_config.LogLevel.WARNING,
            colorize=True,
            serialize=config.logging.json,
            backtrace=True,
            diagnose=True,
        )
    logger.add(
        sys.stderr,
        level=config.logging.level,
        filter=lambda record: record["level"].no >= logging_config.LogLevel.WARNING,
        colorize=True,
        serialize=config.logging.json,
        backtrace=True,
        diagnose=True,
    )
    logger.debug("Logging was setup!")
