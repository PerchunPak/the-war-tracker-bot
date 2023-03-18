"""Module for subscribing to all channels in the database."""
import asyncio

import telethon.tl.functions.channels
import telethon.tl.types
from loguru import logger

from twtb.logic.shared.db import Database


async def run_periodical_subscribing(client: telethon.TelegramClient, bot: telethon.TelegramClient) -> None:
    """Run periodical subscribing to all channels in the database.

    Args:
        client: Telethon's client object. Must not be bot.
        bot: Telethon's bot object. We use it to get information about channels. See comment below in sources.
    """
    logger.trace("Starting periodical subscribing...")
    while True:
        await subscribe_to_all_channels(client, bot)
        await asyncio.sleep(60)


async def subscribe_to_all_channels(client: telethon.TelegramClient, bot: telethon.TelegramClient) -> None:
    """Subscribe to all channels in the database.

    Args:
        client: Telethon's client. Must not be bot.
        bot: Telethon's bot object. We use it to get information about channels. See comment below in sources.
    """
    channels = await Database().get_all_channels()
    for channel in channels:
        # Somewhy, telegram do not want to give us information about channels
        # by id from client account, so we firstly get it from bot account and
        # then use username in subscribe request.
        #
        # It can be quite tricky, as username can be None.
        entity = await bot.get_entity(channel)
        logger.opt(lazy=True).trace(
            "Subscribing to {channel}...",
            channel=lambda: f"{entity.title} ({'@' + entity.username if entity.username else f'ID: {entity.id}'})",
        )
        if entity.username is None:
            logger.warning(
                f"Channel {channel} has no username, skipping from subscribing. Please, report this!"
            )  # TODO can we automatise reporting about this?
            continue

        await client(telethon.tl.functions.channels.JoinChannelRequest(entity.username))
        await client(telethon.tl.functions.account.UpdateNotifySettingsRequest(entity.username))
