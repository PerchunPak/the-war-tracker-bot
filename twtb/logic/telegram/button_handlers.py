"""Module for handlers for buttons in :func:`/start command <twtb.logic.telegram.on_message._start_command>`."""
import abc
import asyncio
import typing as t

import telethon.tl.types
from loguru import logger

from twtb.logic.shared.db import Database
from twtb.logic.shared.db.channels_info import (
    ChannelNotFoundOrIsInvalidError,
    ProvidedIdIsNotAChannelError,
)
from twtb.logic.telegram.data import ButtonData


class ButtonHandler(abc.ABC):
    """Abstract class for button handlers."""

    handles: ButtonData

    async def handle(self, event: telethon.events.CallbackQuery.Event) -> None:
        """Handle button.

        Args:
            event: Telethon's event.
        """
        logger.trace(f"Handling {event.data} button with {type(self).__name__} from {event.sender_id}.")
        return await self._handle(event)

    @abc.abstractmethod
    async def _handle(self, event: telethon.events.CallbackQuery.Event) -> None:
        ...

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

    async def _handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        try:
            async with event.client.conversation(event.chat) as conversation:
                await conversation.send_message("What word do you want to subscribe to?")
                word = (await conversation.get_response()).text
        except (asyncio.TimeoutError, ValueError):
            logger.trace(f"User {event.sender_id} took too long to respond")
            await event.respond("You took too long to respond :(")
            raise

        database = Database()

        is_subscribed = await database.subscribe_user(event.sender_id, word)
        await event.respond("Done!" if is_subscribed else "You are already subscribed to this word!")


class UnsubscribeFromWordButtonHandler(ButtonHandler):
    """Handler for ``Unsubscribe from word`` button."""

    handles = ButtonData.UNSUBSCRIBE_FROM_WORD

    async def _handle(self, event: telethon.events.CallbackQuery.Event) -> None:
        try:
            async with event.client.conversation(event.chat) as conversation:
                await conversation.send_message("What word do you want to unsubscribe from?")
                word = (await conversation.get_response()).text
        except (asyncio.TimeoutError, ValueError):
            logger.trace(f"User {event.sender_id} took too long to respond")
            await event.respond("You took too long to respond :(")
            raise

        database = Database()

        is_removed = await database.unsubscribe_user(event.sender_id, word)
        await event.respond("Done!" if is_removed else "You are not subscribed to this word!")
        logger.trace(
            f"User {event.sender_id} {f'is unsubscribed from the word {word!r}' if is_removed else f'was not subscribed to the word {word!r}, but tried to unsubscribe.'}"
        )


class ListMySubscribesButtonHandler(ButtonHandler):
    """Handler for ``List my subscribes`` button."""

    handles = ButtonData.LIST_MY_SUBSCRIBES

    async def _handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        database = Database()
        subscribes = await database.get_user_words(event.sender_id)

        if len(subscribes) == 0:
            await event.respond("You are not subscribed to anything yet!")
            return

        await event.respond("Your subscribes:\n" + "\n".join(subscribes))


class ListKnownChannelsButtonHandler(ButtonHandler):
    """Handler for ``List known channels`` button."""

    handles = ButtonData.LIST_KNOWN_CHANNELS

    async def _handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        database = Database()
        channels = await database.get_all_channels()

        if len(channels) == 0:
            logger.warning("No channels were added yet!")
            await event.respond("No channels were added yet!")
            return

        human_friendly_names: t.List[str] = []
        for channel in channels:
            entity = await database.channels_info.get_and_save(channel, event.client)
            human_friendly_names.append(f"{entity.title} (@{entity.username})")

        await event.respond("Known channels:\n" + "\n".join(human_friendly_names))


class AddChannelButtonHandler(ButtonHandler):
    """Handler for ``Add channel`` button."""

    handles = ButtonData.ADD_CHANNEL

    async def _handle(self, event: telethon.events.CallbackQuery.Event) -> None:  # noqa: D102
        try:
            async with event.client.conversation(event.chat) as conversation:
                await conversation.send_message("What channel do you want to add?")
                channel = (await conversation.get_response()).text
        except (asyncio.TimeoutError, ValueError):
            logger.trace(f"User {event.sender_id} took too long to respond")
            await event.respond("You took too long to respond :(")
            raise

        database = Database()

        try:
            entity = await database.channels_info.get_and_save(channel, event.client)
        except ChannelNotFoundOrIsInvalidError:
            logger.trace(f"Channel {channel!r} that gave {event.sender.username!r} was not found.")
            await event.respond("Channel not found!")
            return
        except ProvidedIdIsNotAChannelError as exception:
            logger.trace(
                f"Channel {exception.channel_name!r} that gave {event.sender_id} is not a channel, but is {exception.actual_type_name}."
            )
            await event.respond("This is not a channel!")
            return

        is_added = await database.add_channel(entity.username)
        await event.respond("Done!" if is_added else "This channel is already added!")
