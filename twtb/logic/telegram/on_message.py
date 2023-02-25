"""Module for ``on_message`` hook."""
import asyncio

import telethon.events

from twtb.logic.db import Database
from twtb.logic.shared.message_handler import MessageHandler


def register(client: telethon.TelegramClient) -> None:
    """Register the :func:`._on_message` hook.

    Args:
        client: Telethon's client.
    """
    loop = asyncio.get_event_loop()
    database = Database()

    client.on(telethon.events.NewMessage(chats=loop.run_until_complete(database.get_all_channels())))(_on_message)
    client.on(telethon.events.NewMessage(pattern=r"!subscribe (\w+)"))(_subscribe_to_word_command)
    client.on(telethon.events.NewMessage(pattern=r"!add (\w+)"))(_add_channel_command)


async def _on_message(event: telethon.events.NewMessage.Event) -> None:
    """Hook for ``on_message`` event."""
    await MessageHandler().handle(event.message.message, event.message)


async def _subscribe_to_word_command(event: telethon.events.NewMessage.Event) -> None:
    """``!subscribe`` command. Subscribes user to word."""
    channel = event.pattern_match.group(1)
    database = Database()

    await database.subscribe_user(event.chat.id, channel)
    await event.respond("Done!")


async def _add_channel_command(event: telethon.events.NewMessage.Event) -> None:
    """``!add`` command. Adds channel to the database."""
    channel = event.pattern_match.group(1)
    database = Database()

    await database.add_chanel(channel)
    await event.respond("Done!")
