"""Shared abstractions for the all logic."""
import abc
import typing as t

import telethon
from telethon.tl.custom.message import Message as TelethonMessage


class AbstractSender(abc.ABC):
    """Abstraction for the class, that will send a message to users."""

    def __init__(self, bot: telethon.TelegramClient) -> None:
        self._bot = bot

    @abc.abstractmethod
    async def send_message(self, users_ids: t.List[int], message: TelethonMessage) -> None:
        """Send message to users.

        Args:
            users_ids: List of user IDs, which need to get the message.
            message: Telegram message object to send.
        """
