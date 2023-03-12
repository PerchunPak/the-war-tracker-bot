"""Module for subscribing to all channels in the database."""
import telethon.tl.functions.channels
import telethon.tl.types

from twtb.logic.shared.db import Database


async def subscribe_to_all_channels(client: telethon.TelegramClient) -> None:
    """Subscribe to all channels in the database.

    Args:
        client: Telethon's client. Must not be bot.
    """
    channels = await Database().get_all_channels()
    for channel in channels:
        await client(telethon.tl.functions.channels.JoinChannelRequest(channel))
