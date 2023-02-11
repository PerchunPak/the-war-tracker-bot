"""Module for Telegram-relative settings."""
import dataclasses


@dataclasses.dataclass
class TelegramConfigSection:
    """Config for telegram specific settings."""

    api_id: int = "???"  # type: ignore[assignment]
    api_hash: str = "???"
    phone: str = "???"
    password: str = "???"
