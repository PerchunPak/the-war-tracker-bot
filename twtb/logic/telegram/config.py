"""Module for Telegram-relative settings."""
import abc
import dataclasses
import typing as t


@dataclasses.dataclass
class ClientOrBotSection(abc.ABC):
    """Base class for client and bot sections."""

    api_id: int = "???"  # type: ignore[assignment]
    api_hash: str = "???"


@dataclasses.dataclass
class ClientSection(ClientOrBotSection):
    """Config for client specific settings."""

    phone: str = "???"
    password: t.Optional[str] = None


@dataclasses.dataclass
class BotSection(ClientOrBotSection):
    """Config for bot specific settings."""

    bot_token: str = "???"


@dataclasses.dataclass
class TelegramConfigSection:
    """Config for telegram specific settings."""

    client: ClientSection = dataclasses.field(default_factory=ClientSection)
    bot: BotSection = dataclasses.field(default_factory=BotSection)
