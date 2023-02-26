"""Module for ``on_message`` hook."""

import telethon.events

from twtb.logic.shared.db import Database
from twtb.logic.shared.message_handler import MessageHandler


def register(client: telethon.TelegramClient) -> None:
    """Register the :func:`._on_message` hook.

    Args:
        client: Telethon's client.
    """
    client.on(telethon.events.NewMessage())(_on_message)
    client.on(telethon.events.NewMessage(pattern=r"!subscribe (\w+)"))(_subscribe_to_word_command)
    client.on(telethon.events.NewMessage(pattern=r"!add (\w+)"))(_add_channel_command)


async def _on_message(event: telethon.events.NewMessage.Event) -> None:
    """Hook for ``on_message`` event."""
    database = Database()
    channels = await database.get_all_channels()
    if event.chat_id not in channels:
        return

    await MessageHandler().handle(event.message.message, event.message)


async def _subscribe_to_word_command(event: telethon.events.NewMessage.Event) -> None:
    """``!subscribe`` command. Subscribes user to word."""
    word = event.pattern_match.group(1)
    database = Database()

    await database.subscribe_user(event.chat_id, word)
    await event.respond("Done!")


async def _add_channel_command(event: telethon.events.NewMessage.Event) -> None:
    """``!add`` command. Adds channel to the database."""
    channel = event.pattern_match.group(1)
    channel_id = await event.client.get_entity(channel)
    database = Database()

    await database.add_chanel(channel_id.id)
    await event.respond("Done!")
