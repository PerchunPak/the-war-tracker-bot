"""Module for :class:`.TelegramSender`."""
import typing as t

from telethon.tl.custom.message import Message as TelethonMessage

from twtb.logic.shared.abstractions import AbstractSender
from twtb.logic.shared.db import Database


class TelegramSender(AbstractSender):
    """Realisation of :class:`~twtb.logic.shared.abstractions.AbstractSender` for Telegram."""

    async def _send_message(self, users_ids: t.Set[int], message: TelethonMessage) -> None:
        """Send message to users.

        Args:
            users_ids: List of user IDs, which need to get the message.
            message: Telegram message object to send.
        """
        db = Database()
        is_duplicate = await db.sharing_message.set(db.sharing_message.hash_message(message), users_ids)
        if not is_duplicate:
            await message.forward_to(await db.sharing_message.get_shared_chat(client=True))
