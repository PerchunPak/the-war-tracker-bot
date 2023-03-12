"""Module for buttons' data."""
import enum


@enum.unique
class ButtonData(enum.Enum):
    """Data for buttons, that then is sent to callbacks."""

    @staticmethod
    def _generate_next_value_(name: str, *_) -> bytes:
        return name.encode()

    SUBSCRIBE_TO_WORD: bytes = enum.auto()  # type: ignore[assignment]
    UNSUBSCRIBE_FROM_WORD: bytes = enum.auto()  # type: ignore[assignment]
    LIST_MY_SUBSCRIBES: bytes = enum.auto()  # type: ignore[assignment]
    LIST_KNOWN_CHANNELS: bytes = enum.auto()  # type: ignore[assignment]
    ADD_CHANNEL: bytes = enum.auto()  # type: ignore[assignment]
