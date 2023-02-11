"""Shared abstractions for the all logic."""
import abc
import typing as t

from telethon.tl.custom.message import Message as TelethonMessage


class AbstractSender(abc.ABC):
    """Abstraction for the class, that will send a message to users."""

    @abc.abstractmethod
    async def send_message(self, users_ids: t.List[t.Union[int, str]], message: TelethonMessage) -> None:
        """Send message to users.

        Args:
            users_ids: List of user IDs, which need to get the message.
            message: Telegram message object to send.
        """
