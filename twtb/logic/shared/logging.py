"""Module for logging config section."""
import dataclasses
from enum import IntEnum


class LogLevel(IntEnum):
    """Log level for the addon."""

    TRACE = 5
    """Use only for tracing error without a debugger."""
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclasses.dataclass
class LoggingConfigSection:
    """Part of config for logging."""

    level: LogLevel = LogLevel.INFO
    """Log level for the app."""
    json: bool = False
    """Transform logs into JSON."""
