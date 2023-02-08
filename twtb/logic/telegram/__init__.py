"""Package for the Telegram related logic."""
import asyncio

import telethon

from twtb import config as config_module


async def run(client: telethon.TelegramClient) -> None:
    """Actually run the TG bot."""
    await asyncio.sleep(1000)  # todo remove


async def start() -> None:
    """Start the bot, but do not attach to the process."""
    tg_config = config_module.Config().telegram

    asyncio.create_task(
        run(
            await telethon.TelegramClient("anon", tg_config.api_id, tg_config.api_hash).start(
                lambda: tg_config.phone, lambda: tg_config.password
            ),
        ),
    )
