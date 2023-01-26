"""Module for abstractions of the logic app."""
import abc

from twtb.logic.models import (
    AbstractDataclass,
    AbstractMessage,
    AbstractToHandle,
    AbstractToSend,
    ForwardInfo,
)


class AbstractSourceAPI(abc.ABC):
    """API for getting messages from the source."""


class AbstractTextExtractor(abc.ABC):
    """Class for extracting text from source responses."""

    @abc.abstractmethod
    def extract(self, message: AbstractMessage) -> str:
        """Extracts text from source response.

        Args:
            message: Message to extract text from.

        Returns:
            Extracted raw text.
        """


class AbstractSendAPI(abc.ABC):
    """API for sending messages to the user."""

    @abc.abstractmethod
    def forward(self, forward_info: ForwardInfo) -> None:
        """Forwards message to the user.

        Args:
            forward_info: Info to forward.
        """
