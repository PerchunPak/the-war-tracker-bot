"""An empty module for future database system.

Currently, there is no need to implement it now.
"""
import asyncio
import dataclasses
import json
import re
import typing as t

import redis.asyncio as redis
import telethon
import typing_extensions as te
from loguru import logger

import twtb.config
import twtb.utils

TELEGRAM_USERNAME_REGEX = re.compile(r"^[a-zA-Z_0-9]+$")


def _remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def _remove_suffix(string: str, suffix: str) -> str:
    if string.endswith(suffix):
        return string[: len(suffix) * -1]
    return string


def _optimize_channel_id(id: str) -> str:
    before = id

    id = id.lower()
    for prefix in ["https://", "http://", "@", "t.me/"]:
        id = _remove_prefix(id, prefix)
    id = _remove_suffix(id, ".t.me")

    if not re.match(TELEGRAM_USERNAME_REGEX, id):
        logger.error(f"Can't optimize channel ID properly: {before!r} -> {id!r}")

    return id


class Database(metaclass=twtb.utils.Singleton):
    """Main class for the data storage (aka database)."""

    def __init__(self) -> None:
        logger.info("Starting database")
        self._config = twtb.config.Config()
        self._connection: redis.Redis[bytes] = redis.Redis(
            host=self._config.db.host,
            port=self._config.db.port,
            password=self._config.db.password,
        )
        self.channels_info = ChannelInfoInDB(self._connection)

        asyncio.ensure_future(self._connection.ping())

    async def subscribe_user(self, user: int, word: str) -> None:
        """Subscribe user to the word."""
        logger.debug(f"Subscribing {user} to {word=}")
        await self._connection.sadd(f"user_words:{user}", word)

    async def unsubscribe_user(self, user: int, word: str) -> bool:
        """Unsubscribe user from the word.

        Returns:
            Whether word was removed.
        """
        logger.debug(f"Unsubscribing {user} from {word=}")
        return bool(await self._connection.srem(f"user_words:{user}", 0, word))

    async def add_channel(self, id: str) -> None:
        """Add channel to our database."""
        id = _optimize_channel_id(id)
        logger.info(f"Adding channel {id} to our database")
        await self._connection.sadd("channels", id)

    async def get_all_channels(self) -> t.List[str]:
        """Get all channels from database."""
        return list(map(lambda e: e.decode(), await self._connection.smembers("channels")))

    async def get_user_words(self, user_id: int) -> t.List[str]:
        """Get all words, which the user is subscribed to."""
        return t.cast(
            t.List[str], list(map(lambda e: e.decode(), await self._connection.smembers(f"user_words:{user_id}")))
        )

    async def get_all_subscribed_words(self) -> t.Dict[str, t.List[int]]:
        """Get all words, that we need to listen.

        Returns:
            A :class:`dict` where key is a word to listen, and value - a :class:`list` of users to forward message.
        """
        logger.trace("Getting all subscribed words")  # This is kind of expensive operation, so it should be logged

        user_to_words: t.Dict[int, t.List[str]] = {
            (decoded_id := int(user_id[11:].decode())): await self.get_user_words(decoded_id)
            for user_id in await self._connection.keys("user_words:*")
        }

        result: t.Dict[str, t.List[int]] = {}

        for user_to_send, user_words in user_to_words.items():
            for word in user_words:
                if result.get(word) is None:
                    result[word] = [user_to_send]
                    continue
                result[word].append(user_to_send)

        return result


@dataclasses.dataclass
class ChannelInfo:
    """Database configuration section."""

    title: str
    username: str

    def to_json(self) -> str:
        """Transforms self to JSON string."""
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def from_json(cls, data: str) -> te.Self:
        """Creates instance from JSON string."""
        parsed = json.loads(data)
        return cls(title=parsed["title"], username=parsed["username"])

    def __post_init__(self) -> None:
        """The annotations in telethon say that username can be None.

        This will check for that, and report into logs.
        """
        if self.username is None:
            logger.warning(f"Channel {self.title!r} doesn't have username, please report this!")  # type: ignore[unreachable]


class ChannelInfoInDB(metaclass=twtb.utils.Singleton):
    """Class for storing channel info in database."""

    def __init__(self, connection: "redis.Redis[bytes]") -> None:
        self._connection = connection

    async def get(self, id: str) -> t.Optional[ChannelInfo]:
        """Get channel info from database."""
        id = _optimize_channel_id(id)
        as_json = await self._connection.get(f"channel_info:{id}")
        return ChannelInfo.from_json(as_json.decode()) if as_json is not None else as_json

    async def set(self, id: str, value: ChannelInfo, *, expire: t.Optional[float] = None) -> None:
        """Set channel info in database."""
        id = _optimize_channel_id(id)
        await self._connection.set("channel_info:" + id, value.to_json(), ex=expire)

    async def get_and_save(self, id: str, client: telethon.TelegramClient) -> ChannelInfo:
        """Get channel info from database, and save it if it's not there."""
        channel_info = await self.get(id)
        if channel_info is None:
            tg_entity = await client.get_entity(id)

            channel_info = ChannelInfo(title=tg_entity.title, username=tg_entity.username)

            await self.set(id, channel_info, expire=604800)  # 7 days

        return channel_info


@dataclasses.dataclass
class DatabaseConfigSection:
    """Database configuration section."""

    host: str = "localhost"
    port: int = 6379
    password: t.Optional[str] = None
