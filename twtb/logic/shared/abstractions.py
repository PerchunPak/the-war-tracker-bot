"""Shared abstractions for the all logic."""
import abc
import typing as t

import telethon
from loguru import logger
from telethon.tl.custom.message import Message as TelethonMessage


class AbstractSender(abc.ABC):
    """Abstraction for the class, that will send a message to users."""

    def __init__(self, bot: telethon.TelegramClient) -> None:
        self._bot = bot

    async def send_message(self, users_ids: t.List[int], message: TelethonMessage) -> None:
        """Send message to users.

        Args:
            users_ids: List of user IDs, which need to get the message.
            message: Telegram message object to send.
        """
        logger.debug(f"Sending message {message.id} by {message.sender_id} to {users_ids}")
        return await self._send_message(users_ids, message)

    @abc.abstractmethod
    async def _send_message(self, users_ids: t.List[int], message: TelethonMessage) -> None:
        ...
