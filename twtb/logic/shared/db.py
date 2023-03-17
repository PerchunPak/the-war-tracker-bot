"""An empty module for future database system.

Currently, there is no need to implement it now.
"""
import asyncio
import dataclasses
import typing as t

import redis.asyncio as redis
from loguru import logger

import twtb.config
import twtb.utils


class Database(metaclass=twtb.utils.Singleton):
    """Main class for the data storage (aka database)."""

    _CHANNELS_KEY = ""
    """We use disallowed symbols in Telegram nickname, so it can't be overwrote.

    And for the best speed - empty string is the best.
    """

    def __init__(self) -> None:
        logger.info("Starting database")
        self._config = twtb.config.Config()
        self._connection: redis.Redis[bytes] = redis.Redis(
            host=self._config.db.host, port=self._config.db.port, password=self._config.db.password
        )

        asyncio.ensure_future(self._connection.ping())

    async def subscribe_user(self, user: str, word: str) -> None:
        """Subscribe user to the word."""
        logger.debug(f"Subscribing {user} to {word=}")
        await self._connection.rpush(user, word)

    async def unsubscribe_user(self, user: str, word: str) -> bool:
        """Unsubscribe user from the word.

        Returns:
            Whether word was removed.
        """
        logger.debug(f"Unsubscribing {user} from {word=}")
        return bool(await self._connection.lrem(user, 0, word))

    async def add_channel(self, id: int) -> None:
        """Add channel to our database."""
        logger.info(f"Adding channel {id} to our database")
        await self._connection.rpush(self._CHANNELS_KEY, id)

    async def get_all_channels(self) -> t.List[int]:
        """Get all channels from database."""
        return list(map(lambda e: int(e.decode()), await self._connection.lrange(self._CHANNELS_KEY, 0, -1)))

    async def get_user_words(self, user_id: int) -> t.List[str]:
        """Get all words, which the user is subscribed to."""
        return t.cast(t.List[str], list(map(lambda e: e.decode(), await self._connection.lrange(str(user_id), 0, -1))))

    async def get_all_subscribed_words(self) -> t.Dict[str, t.List[int]]:
        """Get all words, that we need to listen.

        Returns:
            A :class:`dict` where key is a word to listen, and value - a :class:`list` of users to forward message.
        """
        logger.trace("Getting all subscribed words")  # This is kind of expensive operation, so it should be logged

        user_to_words: t.Dict[int, t.List[str]] = {
            (decoded_id := int(user_id.decode())): await self.get_user_words(decoded_id)
            for user_id in await self._connection.keys(f"[^{self._CHANNELS_KEY}]*")
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
class DatabaseConfigSection:
    """Database configuration section."""

    host: str = "localhost"
    port: int = 6379
    password: t.Optional[str] = None
