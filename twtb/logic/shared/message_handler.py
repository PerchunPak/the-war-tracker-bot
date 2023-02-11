"""Module for the :class:`.MessageHandler` class."""
from telethon.tl.custom.message import Message as TelethonMessage

from twtb.logic.shared.message_sender import MessageSender


class MessageHandler:
    """Handles message to know if they should be sent to user."""

    async def handle(self, to_handle: str, message: TelethonMessage) -> None:
        """Handles message to know if they should be sent to user.

        Args:
            to_handle: Message to handle.
            message: Message to forward.
        """
        if "hi" in to_handle:
            await MessageSender().send_message(["me"], message)
