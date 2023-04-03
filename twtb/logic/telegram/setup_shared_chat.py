"""Setup shared chat.

Because the user can't know, what ID has the channel
we ask them to send a random generated token into the
chat where bot and client are, so in that way we get the
ID for both of those.
"""
import asyncio
import dataclasses
import random
import string
import typing as t

from loguru import logger

if t.TYPE_CHECKING:
    from twtb.logic.shared.db.sharing_message import SharingMessageInDB

MESSAGE_TOKEN = "".join(random.choices(string.ascii_letters, k=8))  # random 8 chars length string


async def setup_shared_chat(db: "SharingMessageInDB") -> None:
    """Setup shared chat.

    The function will ask user to write a special token to the shared chat.
    And then, via globals, it will spam into the chat, until the user will
    write the token.
    """
    logger.info("Looks like you have not setup shared chat yet.")
    logger.info(f"Please, login as your client and write '{MESSAGE_TOKEN}' to shared chat.")
    logger.info("I will wait for it!")

    while id_container.bot is None or id_container.client is None:
        logger.warning(
            f"Please, login as your client and write '{MESSAGE_TOKEN}' to shared chat. I will repeat the check in one second."
        )
        await asyncio.sleep(1)

    logger.info("Looks like you have setup shared chat!")
    await db.set_shared_chat(id_container.bot, id_container.client)


@dataclasses.dataclass
class SharedChatIDContainer:
    """Container for shared chat ID.

    It's a global actually, but I don't know how to do it better.
    """

    bot: t.Optional[int] = None
    client: t.Optional[int] = None


id_container = SharedChatIDContainer()
