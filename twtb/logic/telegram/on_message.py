"""Module for ``on_message`` hook."""

import asyncio
import typing as t

import telethon.events.common
from loguru import logger
from telethon.tl.custom import Button

from twtb.logic.shared.db import Database
from twtb.logic.shared.message_handler import MessageHandler
from twtb.logic.telegram.button_handlers import ButtonHandler
from twtb.logic.telegram.data import ButtonData
from twtb.logic.telegram.setup_shared_chat import MESSAGE_TOKEN, id_container


def register(bot: telethon.TelegramClient, client: telethon.TelegramClient) -> None:
    """Register the hooks in this file."""
    logger.trace("Registering hooks...")
    database = Database()

    client.on(telethon.events.NewMessage())(_on_message)
    bot.on(telethon.events.NewMessage(pattern="/start"))(_start_command)
    bot.on(telethon.events.CallbackQuery())(_button_callback)

    # shared chat
    task = asyncio.ensure_future(database.sharing_message.get_shared_chat(bot=True))
    task.add_done_callback(
        lambda task: (
            bot.on(telethon.events.NewMessage(chats=[chat_id]))(_on_shared_chat_message)
            if (chat_id := task.result()) is not None
            else None
        )
    )
    # shared chat adding
    client.on(telethon.events.NewMessage(pattern=MESSAGE_TOKEN))(lambda e: _on_shared_chat_adding_token(e, bot=False))
    bot.on(telethon.events.NewMessage(pattern=MESSAGE_TOKEN))(lambda e: _on_shared_chat_adding_token(e, bot=True))


async def _on_message(event: telethon.events.NewMessage.Event) -> None:
    """Hook for ``on_message`` event."""
    logger.trace(f"New message on client! (id={event.message.id!r})")

    database = Database()
    channels = await database.get_all_channels()
    sender = event.message.sender if event.message.sender is not None else await event.message.get_sender()
    if sender.username is not None and sender.username.lower() not in channels:
        logger.trace(f"Message {event.message.id} (by {sender.username}) is not in subscribed channels.")
        return

    await MessageHandler(event.client).handle(event.message.message, event.message)


async def _on_shared_chat_message(event: telethon.events.NewMessage.Event) -> None:
    """Hook for messages in shared (between client and bot) chat.

    Messages there, bot should send to the users.
    """
    logger.trace(f"New message in shared chat! (id={event.message.id!r})")

    database = Database()
    users_ids = await database.sharing_message.get(database.sharing_message.hash_message(event.message))
    for user_id in users_ids:
        await event.message.forward_to(user_id)


async def _on_shared_chat_adding_token(event: telethon.events.NewMessage.Event, *, bot: bool) -> None:
    logger.trace(
        f"New message for registering shared chat! (id={event.message.id!r} {bot=} {MESSAGE_TOKEN=} chat_id={event.message.chat_id!r})"
    )

    if bot:
        id_container.bot = event.message.chat_id
    else:
        id_container.client = event.message.chat_id


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
    logger.trace(f"{event.sender_id} used /start")
    await event.respond(**_get_slash_start_message())


async def _button_callback(event: telethon.events.CallbackQuery.Event) -> None:
    logger.trace(f"{event.sender_id} used button with {event.data=}")
    await ButtonHandler.get_handler(ButtonData(event.data)).handle(event)
    await event.respond(**_get_slash_start_message())
