"""Module for subscribing to all channels in the database."""
import asyncio
import typing as t

import telethon.tl.functions.channels
import telethon.tl.types
from loguru import logger

from twtb.logic.shared.db import Database


async def run_periodical_subscribing(client: telethon.TelegramClient) -> None:
    """Run periodical subscribing to all channels in the database.

    Args:
        client: Telethon's client object. Must not be bot.
    """
    logger.trace("Starting periodical subscribing...")
    while True:
        asyncio.create_task(subscribe_to_all_channels(client))
        await asyncio.sleep(60)


async def subscribe_to_all_channels(client: telethon.TelegramClient) -> None:
    """Subscribe to all channels in the database.

    Args:
        client: Telethon's client. Must not be bot.
    """
    logger.trace("Subscribing to all channels...")
    channels = await Database().get_all_channels()

    if len(channels) == 0:
        logger.warning("No channels were added yet!")
        return

    channels_info = await get_info_about_channels(client, set(channels))

    for channel in map(lambda channel: channel.username, filter(lambda channel: channel.left, channels_info)):  # type: ignore[no-any-return]
        logger.trace(f"Subscribing to {channel}...")

        await client(telethon.tl.functions.channels.JoinChannelRequest(channel))  # subscribe
        await client(
            telethon.tl.functions.account.UpdateNotifySettingsRequest(
                peer=channel, settings=telethon.tl.types.InputPeerNotifySettings(mute_until=2**31 - 1)
            )
        )  # disable notifications
        await client.edit_folder(channel, 1)  # move to archive


async def get_info_about_channels(
    client: telethon.TelegramClient, channels: t.Set[str]
) -> t.Set[telethon.tl.types.TypeChat]:
    """Get info about channels from Telegram.

    Args:
        client: Telethon's client.
        channels: A list of channels to get info about.

    Returns:
        Channels' info.
    """
    try:
        peer_dialogs = await client(telethon.tl.functions.messages.GetPeerDialogsRequest(peers=channels))
    except ValueError as exception:
        if isinstance(exception.__context__, telethon.errors.rpcerrorlist.UsernameNotOccupiedError):
            channel_name = exception.__context__.request.username
            logger.info(f"Added channel {channel_name!r} does not exist!")

            if channel_name in channels:
                await Database().delete_channel(channel_name)
                channels.discard(channel_name)
            else:
                logger.error(f"Channel (that doesn't exist) is not in the database! {channel_name=}")

            return await get_info_about_channels(client, channels)
        raise

    return t.cast(t.Set[telethon.tl.types.TypeChat], peer_dialogs.chats)
