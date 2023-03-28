"""Module for :class:`.TelegramSender`."""
import typing as t

from telethon.tl.custom.message import Message as TelethonMessage

from twtb.logic.shared.abstractions import AbstractSender


class TelegramSender(AbstractSender):
    """Realisation of :class:`~twtb.logic.shared.abstractions.AbstractSender` for Telegram."""

    async def _send_message(self, users_ids: t.Set[int], message: TelethonMessage) -> None:
        """Send message to users.

        Args:
            users_ids: List of user IDs, which need to get the message.
            message: Telegram message object to send.
        """
        # TODO the system doesn't work, because we need to transfer message ID to the bot from client
        # and only then it's possible to forward the message to the user
        return
        # for user_id in users_ids:
        #     await self._bot.forward_messages(user_id, message)
