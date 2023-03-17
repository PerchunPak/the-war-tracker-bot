"""Entrypoint for the whole application."""
from loguru import logger

from twtb.logic.telegram import run as run_tg_bot
from twtb.utils import setup_logging


def main() -> None:
    """The main function, that starts everything."""
    setup_logging()
    logger.info("Hello World!")
    run_tg_bot()


if __name__ == "__main__":
    main()
