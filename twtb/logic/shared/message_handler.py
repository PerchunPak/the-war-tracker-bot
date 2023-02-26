"""Module for the :class:`.MessageHandler` class."""
from telethon.tl.custom.message import Message as TelethonMessage

from twtb.logic.shared.db import Database
from twtb.logic.shared.message_sender import MessageSender


class MessageHandler:
    """Handles message to know if they should be sent to user."""

    def __init__(self) -> None:
        self._db = Database()
        self._sender = MessageSender()

    async def handle(self, to_handle: str, message: TelethonMessage) -> None:
        """Handles message to know if they should be sent to user.

        Args:
            to_handle: Message to handle.
            message: Message to forward.
        """
        words_to_look_for = await self._db.get_all_subscribed_words()

        for word, users in words_to_look_for.items():
            if word in to_handle:
                await self._sender.send_message(users, message)
