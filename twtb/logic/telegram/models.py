"""Models for Telegram part of the application."""
from twtb.logic.models import AbstractMessage, AbstractToHandle, AbstractToSend


class TelegramMessage(AbstractMessage):
    """Model for Telegram messages."""


class TelegramToHandle(AbstractToHandle):
    """Model for Telegram messages to handle."""


class TelegramToSend(AbstractToSend):
    """Model for Telegram messages to send."""
