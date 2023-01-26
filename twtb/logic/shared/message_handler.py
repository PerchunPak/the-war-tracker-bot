"""Module for the :class:`.MessageHandler` class."""
import typing as t

from twtb.logic.models import AbstractToHandle, AbstractToSend


class MessageHandler:
    """Handles message to know if they should be sent to user."""

    def handle(self, to_handle: AbstractToHandle) -> t.Optional[AbstractToSend]:
        """Handles message to know if they should be sent to user.

        Args:
            to_handle: Message to handle.
        """
        raise NotImplementedError("This is in TODO now.")
