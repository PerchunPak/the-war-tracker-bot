"""Module for abstract models of the logic app."""
import abc
from dataclasses import dataclass


@dataclass
class AbstractDataclass(abc.ABC):
    """Prevents instantiation of abstract dataclasses.

    Got this from https://stackoverflow.com/a/60669138/20952782.
    """

    def __new__(cls, *args, **kwargs) -> "AbstractDataclass":
        """Prevents instantiation of abstract dataclasses."""
        if cls == AbstractDataclass or cls.__bases__[0] == AbstractDataclass:
            raise TypeError("Cannot instantiate abstract dataclass.")
        return super().__new__(cls)


@dataclass
class AbstractMessage(AbstractDataclass):
    """Abstract model for messages.

    :class:`SourceAPI <AbstractSourceAPI>` -> :class:`TextExtractor <AbstractTextExtractor>`.
    """


@dataclass
class AbstractToHandle(AbstractDataclass):
    """Abstract model for messages to handle.

    :class:`TextExtractor <AbstractTextExtractor>` -> :class:`MessageHandler <AbstractMessageHandler>`.
    """

    forward_info: "ForwardInfo"
    message: str


@dataclass
class AbstractToSend(AbstractDataclass):
    """Abstract model for messages to send.

    :class:`MessageHandler <AbstractMessageHandler>` -> :class:`UserSender <AbstractUserSender>`.
    """

    forward_info: "ForwardInfo"


@dataclass
class ForwardInfo:
    """Model for containing info to forward."""
