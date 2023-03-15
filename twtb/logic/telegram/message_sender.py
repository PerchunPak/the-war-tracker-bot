"""Module for :class:`.TelegramSender`."""
import typing as t

from telethon.tl.custom.message import Message as TelethonMessage

from twtb.logic.shared.abstractions import AbstractSender


class TelegramSender(AbstractSender):
    """Realisation of :class:`~twtb.logic.shared.abstractions.AbstractSender` for Telegram."""

    async def send_message(self, users_ids: t.List[int], message: TelethonMessage) -> None:
        """Send message to users.

        Args:
            users_ids: List of user IDs, which need to get the message.
            message: Telegram message object to send.
        """
        for user_id in users_ids:
            await self._bot.forward_messages(user_id, message)
