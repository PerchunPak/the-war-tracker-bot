"""Module for :class:`.MessageSender`."""
import functools
import typing as t

import telethon
from telethon.tl.custom.message import Message as TelethonMessage

from twtb.logic.shared.abstractions import AbstractSender


class MessageSender:
    """Iterates over all realisations of :class:`~twtb.logic.shared.abstractions.AbstractSender` and calls them."""

    def __init__(self, bot: telethon.TelegramClient) -> None:
        self._bot = bot

    @functools.cached_property
    def _senders(self) -> t.List[AbstractSender]:
        """Getter for list of realisations of :class:`~twtb.logic.shared.abstractions.AbstractSender`."""
        from twtb.logic.telegram.message_sender import TelegramSender

        return [TelegramSender(self._bot)]

    async def send_message(self, users_ids: t.List[int], message: TelethonMessage) -> None:
        """Iterate over all realisations of :class:`~twtb.logic.shared.abstractions.AbstractSender` and call them.

        Args:
            users_ids: List of user IDs, which need to get the message.
            message: Telegram message object to send.
        """
        for sender in self._senders:
            await sender.send_message(users_ids, message)
