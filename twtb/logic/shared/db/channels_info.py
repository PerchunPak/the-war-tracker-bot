"""Module for :attr:`~twtb.logic.shared.db.Database.channels_info` attribute."""
import dataclasses
import json
import typing as t

import redis.asyncio as redis
import telethon
import typing_extensions as te
from loguru import logger

import twtb.logic.shared.db as db_pkg
import twtb.utils


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
        id = db_pkg._optimize_channel_id(id)
        as_json = await self._connection.get(f"channel_info:{id}")
        return ChannelInfo.from_json(as_json.decode()) if as_json is not None else as_json

    async def set(self, id: str, value: ChannelInfo, *, expire: t.Optional[float] = None) -> None:
        """Set channel info in database."""
        id = db_pkg._optimize_channel_id(id)
        await self._connection.set("channel_info:" + id, value.to_json(), ex=expire)

    async def get_and_save(self, id: str, client: telethon.TelegramClient) -> ChannelInfo:
        """Get channel info from database, and save it if it's not there."""
        channel_info = await self.get(id)
        if channel_info is None:
            tg_entity = await client.get_entity(id)

            channel_info = ChannelInfo(title=tg_entity.title, username=tg_entity.username)

            await self.set(id, channel_info, expire=604800)  # 7 days

        return channel_info
