"""Module for ``on_message`` hook."""

import typing as t

import telethon.events.common
from telethon.tl.custom import Button

from twtb.logic.shared.db import Database
from twtb.logic.shared.message_handler import MessageHandler
from twtb.logic.telegram.button_handlers import ButtonHandler
from twtb.logic.telegram.data import ButtonData


def register(client: telethon.TelegramClient) -> None:
    """Register the :func:`._on_message` hook.

    Args:
        client: Telethon's client.
    """
    client.on(telethon.events.NewMessage())(_on_message)
    client.on(telethon.events.NewMessage(pattern="/start"))(_start_command)
    client.on(telethon.events.CallbackQuery())(_button_callback)


async def _on_message(event: telethon.events.NewMessage.Event) -> None:
    """Hook for ``on_message`` event."""
    database = Database()
    channels = await database.get_all_channels()
    if event.chat_id not in channels:
        return

    await MessageHandler(event.client).handle(event.message.message, event.message)


def _get_slash_start_message() -> t.Dict[str, t.Any]:  # type: ignore[misc] # Explicit "Any" is not allowed
    return {
        "message": "Hello! I'm The War Tracker Bot, I will notify you for any changes in the war!",
        "buttons": [
            [
                Button.inline("Subscribe to word", ButtonData.SUBSCRIBE_TO_WORD.value),
                Button.inline("Unsubscribe from word", ButtonData.UNSUBSCRIBE_FROM_WORD.value),
            ],
            [
                Button.inline("List my subscribes", ButtonData.LIST_MY_SUBSCRIBES.value),
                Button.inline("List known channels", ButtonData.LIST_KNOWN_CHANNELS.value),
            ],
            [Button.inline("Add channel", ButtonData.ADD_CHANNEL.value)],
        ],
    }


async def _start_command(event: telethon.events.NewMessage.Event) -> None:
    await event.respond(**_get_slash_start_message())


async def _button_callback(event: telethon.events.CallbackQuery.Event) -> None:
    await ButtonHandler.get_handler(ButtonData(event.data)).handle(event)
    await event.respond(**_get_slash_start_message())
