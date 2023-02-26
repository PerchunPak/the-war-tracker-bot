"""An empty module for future database system.

Currently, there is no need to implement it now.
"""
import typing as t

import twtb.utils


class Database(metaclass=twtb.utils.Singleton):
    """An empty class for future database system.

    Todo:
        There are only a few methods, that I can came up with now.
        In the progress, I will add more methods, that need to be implemented.
    """

    async def subscribe_user(self, user_id: int, word: str) -> None:
        """Subscribe user to the word."""

    async def add_chanel(self, id: str) -> None:
        """Add channel to our database."""

    async def get_all_channels(self) -> t.List[str]:  # type: ignore[empty-body]
        """Get all channels from database."""

    async def get_user_subscribes(self, user_id: int) -> t.List[str]:  # type: ignore[empty-body]
        """Get all words, which the user is subscribed to."""

    async def get_all_subscribed_words(self) -> t.Dict[str, t.List[str]]:
        """Get all words, that we need to listen.

        Returns:
            A :class:`dict` where key is a word to listen, and value - a list of users to forward message.
        """
        user_to_words: t.Dict[str, t.Awaitable[t.List[str]]] = {  # type: ignore[var-annotated]
            user_id: self.get_user_subscribes(user_id) for user_id in []  # TODO db logic
        }

        result: t.Dict[str, t.List[str]] = {}

        for user_to_send, get_their_words in user_to_words.items():
            for word in await get_their_words:
                if result.get(word) is None:
                    result[word] = [user_to_send]
                    continue
                result[word].append(user_to_send)

        return result
