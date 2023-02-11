"""Module for ``on_message`` hook."""
import telethon.events

from twtb.logic.shared.message_handler import MessageHandler


def register(client: telethon.TelegramClient) -> None:
    """Register the ``on_message`` hook.

    Args:
        client: Telethon's client.
    """
    client.on(telethon.events.NewMessage())(_on_message)


async def _on_message(event: telethon.events.NewMessage.Event) -> None:
    """Hook for ``on_message`` event."""
    await MessageHandler().handle(event.message.message, event.message)
