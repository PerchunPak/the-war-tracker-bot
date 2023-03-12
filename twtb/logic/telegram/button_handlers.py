"""Module for handlers for buttons in :func:`/start command <twtb.logic.telegram.on_message._start_command>`."""
import abc
import asyncio
import typing as t

import telethon.events
import telethon.tl.functions.channels
import telethon.tl.types
from telethon.tl.types import Channel

from twtb.logic.shared.db import Database
from twtb.logic.telegram.data import ButtonData


class ButtonHandler(abc.ABC):
    """Abstract class for button handlers."""

    handles: ButtonData

    @abc.abstractmethod
    async def handle(self, event: telethon.events.CallbackQuery.Event) -> None:
        """Handle button.

        Args:
            event: Telethon's event.
        """

    @classmethod
    def get_handler(cls, button_data: ButtonData) -> "ButtonHandler":
        """Get handler for button.

        Args:
            button_data: Button data.

        Returns:
            Handler for button.
        """
        for possible_handler in cls.__subclasses__():
            if possible_handler.handles == button_data:
                return possible_handler()
        raise NotImplementedError(f"Button handler for {button_data!r} is not implemented")


class SubscribeToWordButtonHandler(ButtonHandler):
    """Handler for ``Subscribe to word`` button."""

    handles = ButtonData.SUBSCRIBE_TO_WORD

    async def handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        try:
            async with event.client.conversation(event.chat) as conversation:
                await conversation.send_message("What word do you want to subscribe to?")
                word = (await conversation.get_response()).text
        except (asyncio.TimeoutError, ValueError):
            await event.respond("You took too long to respond :(")
            raise

        database = Database()

        await database.subscribe_user(event.chat_id, word)
        await event.respond("Done!")


class UnsubscribeFromWordButtonHandler(ButtonHandler):
    """Handler for ``Unsubscribe from word`` button."""

    handles = ButtonData.UNSUBSCRIBE_FROM_WORD

    async def handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        try:
            async with event.client.conversation(event.chat) as conversation:
                await conversation.send_message("What word do you want to unsubscribe from?")
                word = (await conversation.get_response()).text
        except (asyncio.TimeoutError, ValueError):
            await event.respond("You took too long to respond :(")
            raise

        database = Database()

        is_removed = await database.unsubscribe_user(event.chat_id, word)
        await event.respond("Done!" if is_removed else "You are not subscribed to this word!")


class ListMySubscribesButtonHandler(ButtonHandler):
    """Handler for ``List my subscribes`` button."""

    handles = ButtonData.LIST_MY_SUBSCRIBES

    async def handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        database = Database()
        subscribes = await database.get_user_words(event.chat_id)
        await event.respond("Your subscribes:\n" + "\n".join(subscribes))


class ListKnownChannelsButtonHandler(ButtonHandler):
    """Handler for ``List known channels`` button."""

    handles = ButtonData.LIST_KNOWN_CHANNELS

    async def handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        database = Database()
        channels = await database.get_all_channels()

        human_friendly_names: t.List[str] = []
        for channel in channels:
            entity = await event.client.get_entity(channel)
            human_friendly_names.append(
                f"{entity.title} ({'@' + entity.username if entity.username else f'ID: {entity.id}'})"
            )

        await event.respond("Known channels:\n" + "\n".join(human_friendly_names))


class AddChannelButtonHandler(ButtonHandler):
    """Handler for ``Add channel`` button."""

    handles = ButtonData.ADD_CHANNEL

    async def handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        try:
            async with event.client.conversation(event.chat) as conversation:
                await conversation.send_message("What channel do you want to add?")
                raw_channel = (await conversation.get_response()).text
        except (asyncio.TimeoutError, ValueError):
            await event.respond("You took too long to respond :(")
            raise

        try:
            channel = await event.client.get_entity(raw_channel)
        except ValueError:
            await event.respond("Channel not found!")
            return

        if not isinstance(channel, Channel):
            await event.respond("This is not a channel!")
            return

        database = Database()

        await event.client(telethon.tl.functions.channels.JoinChannelRequest(channel))
        await database.add_channel(channel.id)
        await event.respond("Done!")
