"""Entrypoint for the whole application."""
import asyncio
import time

import twtb.config
from twtb.logic.telegram import start as start_tg_bot


async def main() -> None:
    """The main function, that starts everything."""
    config = twtb.config.Config()

    if config.telegram.enabled:
        await start_tg_bot()

    while True:  # todo make normal infinitive loop
        time.sleep(999999)


if __name__ == "__main__":
    asyncio.run(main())
