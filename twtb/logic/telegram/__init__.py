"""Package for the Telegram related logic."""
import telethon.events

from twtb import config as config_module
from twtb.logic.telegram.on_message import register as register_hooks


def run() -> None:
    """Actually run the bot and attach to it."""
    tg_config = config_module.Config().telegram

    client = telethon.TelegramClient("anon", tg_config.api_id, tg_config.api_hash).start(
        lambda: tg_config.phone, lambda: tg_config.password
    )
    get_client._client = client  # type: ignore[attr-defined]
    register_hooks(client)
    with client:
        client.run_until_disconnected()


def get_client() -> telethon.TelegramClient:
    """Getter for :class:`telethon.TelegramClient`."""
    if not hasattr(get_client, "_client"):
        raise RuntimeError("Bot was not initialised!")

    return get_client._client
