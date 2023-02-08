"""File for the main config."""
import dataclasses
import os
import pathlib
import typing as t

import omegaconf
import typing_extensions as te
from omegaconf import dictconfig

from twtb import utils
from twtb.logic.telegram.config import TelegramConfigSection

BASE_DIR = pathlib.Path(__file__).parent.parent


@dataclasses.dataclass
class Config(metaclass=utils.Singleton):
    """The main config that holds everything in itself."""

    telegram: TelegramConfigSection = dataclasses.field(default_factory=TelegramConfigSection)

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
    def _handle_env_variables(cfg: dictconfig.DictConfig) -> None:
        """Process all values, and redef them with values from env variables.

        Args:
            cfg: :py:class:`.Config` instance.
        """
        for key in cfg:
            if str(key).upper() in os.environ:
                cfg[str(key)] = os.environ[str(key).upper()]
