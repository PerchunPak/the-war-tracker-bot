"""Entrypoint for the whole application."""
from twtb.logic.telegram import run as run_tg_bot


def main() -> None:
    """The main function, that starts everything."""
    run_tg_bot()


if __name__ == "__main__":
    main()
