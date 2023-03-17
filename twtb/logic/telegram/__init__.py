"""Package for the Telegram related logic."""
import asyncio

import telethon.events
from loguru import logger

from twtb import config as config_module
from twtb.logic.telegram.on_message import register as register_hooks
from twtb.logic.telegram.subscribe import run_periodical_subscribing


def run() -> None:
    """Actually run the bot and attach to it."""
    logger.trace("Running the Telegram part...")

    tg_config = config_module.Config().telegram
    loop = asyncio.get_event_loop()

    logger.debug("Connecting to bot account...")
    bot = telethon.TelegramClient("bot", tg_config.bot.api_id, tg_config.bot.api_hash).start(
        bot_token=tg_config.bot.bot_token
    )
    logger.debug("Connecting to client account...")
    client = telethon.TelegramClient("client", tg_config.client.api_id, tg_config.client.api_hash).start(
        phone=tg_config.client.phone, password=tg_config.client.password
    )
    logger.info("Connected to bot and client accounts!")

    register_hooks(bot, client)
    loop.create_task(run_periodical_subscribing(client, bot))

    with bot, client:
        try:
            loop.run_until_complete(run_both_client_and_bot(client, bot))
        except KeyboardInterrupt:
            pass
    logger.info("Looks like Telegram part ended the work.")


async def run_both_client_and_bot(client: telethon.TelegramClient, bot: telethon.TelegramClient) -> None:
    """Run both the client and the bot."""
    logger.trace("Running both the client and the bot...")
    done, pending = await asyncio.wait(
        {
            asyncio.create_task(client._run_until_disconnected(), name="Client"),
            asyncio.create_task(bot._run_until_disconnected(), name="Bot"),
        },
        return_when=asyncio.FIRST_COMPLETED,
    )
    logger.info(f"Job(s) ended the work: {' and '.join(task.get_name() for task in done)}.")

    if len(pending) > 0:
        for task in pending:
            logger.warning(f"{task.get_name()} has not ended the work, stopping it")
            task.cancel()
