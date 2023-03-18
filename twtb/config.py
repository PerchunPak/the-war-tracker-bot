"""File for the main config."""
import dataclasses
import os
import pathlib
import typing as t

import omegaconf
import typing_extensions as te
from omegaconf import dictconfig

from twtb import utils
from twtb.logic.shared.db import DatabaseConfigSection
from twtb.logic.shared.logging import LoggingConfigSection
from twtb.logic.telegram.config import TelegramConfigSection

BASE_DIR = pathlib.Path(__file__).parent.parent


@dataclasses.dataclass
class Config(metaclass=utils.Singleton):
    """The main config that holds everything in itself."""

    logging: LoggingConfigSection = dataclasses.field(default_factory=LoggingConfigSection)
    telegram: TelegramConfigSection = dataclasses.field(default_factory=TelegramConfigSection)
    db: DatabaseConfigSection = dataclasses.field(default_factory=DatabaseConfigSection)

    @classmethod
    def _setup(cls) -> te.Self:
        """Set up the config.

        It is just load config from file, also it is rewrite config with merged data.

        Returns:
            :py:class:`.Config` instance.
        """
        config_path = BASE_DIR / "config.yml"
        cfg = omegaconf.OmegaConf.structured(cls)

        if config_path.exists():
            loaded_config = omegaconf.OmegaConf.load(config_path)
            cfg = omegaconf.OmegaConf.merge(cfg, loaded_config)

        with open(config_path, "w") as config_file:
            omegaconf.OmegaConf.save(cfg, config_file)

        cls._handle_env_variables(cfg)

        return t.cast(te.Self, cfg)

    @staticmethod
    def _handle_env_variables(cfg: dictconfig.DictConfig, *, prefix: t.Optional[str] = None) -> None:
        """Process all values, and redef them with values from env variables.

        Args:
            cfg: :py:class:`.Config` instance.
            prefix:
                Prefix for env variable. Example ``prefix="telegram"`` and
                ``key="token"`` will look for ``TELEGRAM_TOKEN``.
        """
        for key in cfg:
            key_to_look_for = f"{prefix}_{key!r}" if prefix else str(key)
            if isinstance(cfg[key], dictconfig.DictConfig):
                Config._handle_env_variables(cfg[key], prefix=key_to_look_for)
                continue

            if key_to_look_for.upper() in os.environ:
                cfg[str(key)] = os.environ[str(key).upper()]
