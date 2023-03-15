"""Package for the Telegram related logic."""
import telethon.events

from twtb import config as config_module
from twtb.logic.telegram.on_message import register as register_hooks
from twtb.logic.telegram.subscribe import subscribe_to_all_channels


def run() -> None:
    """Actually run the bot and attach to it."""
    tg_config = config_module.Config().telegram

    client = telethon.TelegramClient("bot", tg_config.api_id, tg_config.api_hash).start(bot_token=tg_config.bot_token)
    register_hooks(client)
    # client.loop.run_until_complete(subscribe_to_all_channels(client)) # FIXME doesn't work with bot, needs userbot
    with client:
        client.run_until_disconnected()
