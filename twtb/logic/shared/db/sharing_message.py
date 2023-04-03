"""Makes possible sharing messages between client and bot.

Because almost all IDs in Telegram are unique only to one bot.
Here, we firstly send message to the shared chat, from where
bot reforwards message to the end users.

This is the only way to share message ID that I found.
"""
import asyncio
import base64
import struct
import typing as t

import redis.asyncio as redis
from loguru import logger
from telethon.tl.custom.message import Message as TelethonMessage

import twtb.utils
from twtb.logic.telegram.setup_shared_chat import setup_shared_chat


def hash_with_fnv64(string: str) -> str:
    """FNV-1a 64-bit hash implementation.

    It is a fast non-cryptographic hash function, which is good for
    us to transform the message data into short form.

    .. seealso::
        Was copied from `https://gist.github.com/Cilyan/9424144`_ and
        `https://stackoverflow.com/a/22000293`_.
    """
    data = string.encode("utf8", errors="ignore")

    hash = 0xCBF29CE484222325
    for b in data:
        hash *= 0x100000001B3
        hash &= 0xFFFFFFFFFFFFFFFF
        hash ^= b

    # Pack hash (int) into bytes
    bytes_hash = struct.pack("<Q", hash)
    # Encode in base64. There is always a padding "=" at the end, because the
    # hash is always 64bits long. We don't need it.
    return base64.urlsafe_b64encode(bytes_hash)[:-1].decode("ascii")


class SharingMessageInDB(metaclass=twtb.utils.Singleton):
    """Class for sharing message in database."""

    def __init__(self, connection: "redis.Redis[bytes]") -> None:
        self._connection = connection

        asyncio.ensure_future(self._check_shared_chat_availability())

    async def _check_shared_chat_availability(self) -> None:
        id_as_bot, id_as_client = await self.get_shared_chat(both=True)
        if id_as_bot is None or id_as_client is None:
            await setup_shared_chat(self)

    async def get(self, message_hash: str) -> t.Set[int]:
        """Get users to send the message from message's hash."""
        logger.trace(f"Getting users to send the message {message_hash!r} from database...")
        result = await self._connection.smembers(f"sharing_message:{message_hash}")
        if len(result) == 0:
            raise ValueError(f"Message is not found in database. {message_hash=}")

        return set(map(lambda e: int(e), result))

    async def set(self, message_hash: str, users_to_send: t.Set[int]) -> bool:
        """Set users to send the message in database.

        Returns:
            Whether the message is duplicate. The function will raise warning if it's :class:`True <bool>`.
        """
        logger.trace(f"Saving users to send the message {message_hash!r} to database...")
        how_many_were_added = await self._connection.sadd(f"sharing_message:{message_hash}", *users_to_send)

        if how_many_were_added != len(users_to_send):
            logger.warning(
                f"Found the duplicate attempt to send the message {message_hash!r} to {users_to_send=}. {how_many_were_added=} {len(users_to_send)=}"
            )

        await self._connection.expire(
            f"sharing_message:{message_hash}", time=3600  # insure, that dead requests will not stick in database
        )
        return how_many_were_added != len(users_to_send)

    @t.overload
    async def get_shared_chat(self, *, both: bool) -> t.Tuple[t.Optional[int], t.Optional[int]]:  # noqa: D102
        ...

    @t.overload
    async def get_shared_chat(self, *, client: bool) -> t.Optional[int]:  # noqa: D102
        ...

    @t.overload
    async def get_shared_chat(self, *, bot: bool) -> t.Optional[int]:  # noqa: D102
        ...

    async def get_shared_chat(
        self, *, both: t.Optional[bool] = None, client: t.Optional[bool] = None, bot: t.Optional[bool] = None
    ) -> t.Union[t.Tuple[t.Optional[int], t.Optional[int]], t.Optional[int]]:
        """Get shared chat id as bot and client.

        Returns:
            Tuple, where first element is bot's chat id and second is client's chat id.
        """
        assert (
            (both is not None and client is None and bot is None)
            or (client is None and bot is not None)
            or (client is not None and bot is None)
        ), "You called the function wrong!"

        if both:
            return t.cast(
                t.Tuple[t.Optional[int], t.Optional[int]],
                tuple(
                    map(
                        lambda e: int(e) if e is not None else None,
                        await self._connection.mget("shared_chat:bot", "shared_chat:client"),
                    )
                ),
            )
        else:
            result = await self._connection.get(f"shared_chat:{'bot' if bot else 'client'}")
            return int(result) if result is not None else None

    async def set_shared_chat(self, bot_chat_id: int, client_chat_id: int) -> None:
        """Set shared chat id as bot and client."""
        await self._connection.mset(
            {
                "shared_chat:bot": bot_chat_id,
                "shared_chat:client": client_chat_id,
            }
        )

    @staticmethod
    def hash_message(message: TelethonMessage) -> str:
        """Hash message to send."""
        return hash_with_fnv64(message.raw_text)
