"""Module for Sentry config section."""
import dataclasses


@dataclasses.dataclass
class SentryConfigSection:
    """Sentry config section."""

    enabled: bool = True
    dsn: str = "..."
    traces_sample_rate: float = 1.0
