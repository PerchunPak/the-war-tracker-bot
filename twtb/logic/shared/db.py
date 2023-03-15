"""An empty module for future database system.

Currently, there is no need to implement it now.
"""
import dataclasses
import typing as t

import redis.asyncio as redis

import twtb.config
import twtb.utils


class Database(metaclass=twtb.utils.Singleton):
    """Main class for the data storage (aka database)."""

    _CHANNELS_KEY = ""
    """We use disallowed symbols in Telegram nickname, so it can't be overwrote.

    And for the best speed - empty string is the best.
    """

    def __init__(self) -> None:
        self._config = twtb.config.Config()
        self._connection: redis.Redis[bytes] = redis.Redis(
            host=self._config.db.host, port=self._config.db.port, password=self._config.db.password
        )

    async def subscribe_user(self, user: str, word: str) -> None:
        """Subscribe user to the word."""
        await self._connection.rpush(user, word)

    async def unsubscribe_user(self, user: str, word: str) -> bool:
        """Unsubscribe user from the word.

        Returns:
            Whether word was removed.
        """
        return bool(await self._connection.lrem(user, 0, word))

    async def add_channel(self, id: int) -> None:
        """Add channel to our database."""
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
            A :class:`dict` where key is a word to listen, and value - a list of users to forward message.
        """
        user_to_words: t.Dict[int, t.Awaitable[t.List[str]]] = {
            (decoded_id := int(user_id.decode())): self.get_user_words(decoded_id)
            for user_id in await self._connection.keys(f"[^{self._CHANNELS_KEY}]*")
        }

        result: t.Dict[str, t.List[int]] = {}

        for user_to_send, get_their_words in user_to_words.items():
            for word in await get_their_words:
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
