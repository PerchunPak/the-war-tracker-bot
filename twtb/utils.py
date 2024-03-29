"""Module for some of our utils."""
import os
import pathlib
import sys
import typing as t

import sentry_sdk
from loguru import logger

import twtb.logic.shared.logging as logging_config


class Singleton(type):
    """Metaclass to do Singleton pattern."""

    _instances: dict[type, t.Any] = {}  # type: ignore[misc] # Explicit "Any" is not allowed

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


def start_sentry() -> None:
    """Start Sentry listening."""
    # circular imports
    from twtb.config import BASE_DIR, Config

    config = Config()

    if not config.sentry.enabled:
        logger.warning("Sentry is disabled! Errors will not be reported!")
        return

    sentry_sdk.init(
        dsn=config.sentry.dsn,
        traces_sample_rate=config.sentry.traces_sample_rate,
        release=_get_commit(BASE_DIR / "commit.txt"),
        environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
        _experiments={
            "profiles_sample_rate": 1.0,
        },
    )


def _get_commit(commit_txt_path: pathlib.Path) -> t.Optional[str]:
    """Get current commit from ``commit.txt`` file."""
    if not commit_txt_path.exists():
        logger.warning("No commit.txt file found! Sentry will not report release version!")
        return None

    with commit_txt_path.open() as commit_txt_file:
        commit = commit_txt_file.read().strip()
        logger.info(f"Current commit is: {commit}")
        return commit


def remove_prefix(string: str, prefix: str) -> str:
    """Remove prefix from the string."""
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def remove_suffix(string: str, suffix: str) -> str:
    """Remove suffix from the string."""
    if string.endswith(suffix):
        return string[: len(suffix) * -1]
    return string
