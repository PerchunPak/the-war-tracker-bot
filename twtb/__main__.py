"""Entrypoint for the whole application."""
from loguru import logger

import twtb.utils as utils
from twtb.logic.telegram import run as run_tg_bot


def main() -> None:
    """The main function, that starts everything."""
    utils.setup_logging()
    utils.start_sentry()
    logger.info("Hello World!")
    run_tg_bot()


if __name__ == "__main__":
    main()
