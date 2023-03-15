"""Package for the Telegram related logic."""
import asyncio

import telethon.events

from twtb import config as config_module
from twtb.logic.telegram.on_message import register as register_hooks
from twtb.logic.telegram.subscribe import run_periodical_subscribing


def run() -> None:
    """Actually run the bot and attach to it."""
    tg_config = config_module.Config().telegram
    loop = asyncio.get_event_loop()

    bot = telethon.TelegramClient("bot", tg_config.bot.api_id, tg_config.bot.api_hash).start(
        bot_token=tg_config.bot.bot_token
    )
    client = telethon.TelegramClient("client", tg_config.client.api_id, tg_config.client.api_hash).start(
        phone=tg_config.client.phone, password=tg_config.client.password
    )

    register_hooks(bot, client)
    loop.create_task(run_periodical_subscribing(client, bot))

    with bot, client:
        loop.run_until_complete(run_both_client_and_bot(client, bot))


async def run_both_client_and_bot(client: telethon.TelegramClient, bot: telethon.TelegramClient) -> None:
    """Run both the client and the bot."""
    done, pending = await asyncio.wait(
        {
            asyncio.create_task(client._run_until_disconnected(), name="Client"),
            asyncio.create_task(bot._run_until_disconnected(), name="Bot"),
        },
        return_when=asyncio.FIRST_COMPLETED,
    )

    if len(pending) > 0:
        for task in pending:
            task.cancel()

        raise RuntimeError("One of the clients disconnected unexpectedly.")
