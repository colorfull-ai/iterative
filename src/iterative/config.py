from omegaconf import OmegaConf
import os
from nosql_yorm.config import Config as NosqlYormConfig, set_config as set_nosql_yorm_config

class Config:
    def __init__(self, user_config_path=None, merge_config=True):
        # Load the default configuration for iterative
        iterative_default_config_path = os.path.join(os.path.dirname(__file__), 'default_config.yaml')
        self.default_config = OmegaConf.load(iterative_default_config_path) if os.path.exists(iterative_default_config_path) else OmegaConf.create()

        # Load the nosql_yorm default configuration and merge it
        nosql_yorm_config = NosqlYormConfig()
        self.default_config = OmegaConf.merge(self.default_config, nosql_yorm_config.config)

        # Load the user configuration if provided
        self.user_config = OmegaConf.load(user_config_path) if user_config_path and os.path.exists(user_config_path) else OmegaConf.create()

        # Merge configurations
        self.config = OmegaConf.merge(self.default_config, self.user_config) if merge_config else self.user_config

        # Set the merged configuration as the nosql_yorm configuration
        set_nosql_yorm_config(self)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def merge_config(self, other_config):
        """
        Merge another Config instance's configuration into this one.

        Args:
            other_config (Config): Another Config instance to merge.
        """
        if not isinstance(other_config, Config):
            raise ValueError("other_config must be an instance of Config")
        self.config = OmegaConf.merge(self.config, other_config.config)
        set_nosql_yorm_config(self)
        return self

# Global shared configuration instance
_shared_config = Config()

def set_config(config):
    global _shared_config
    _shared_config = config

def get_config():
    global _shared_config
    return _shared_config
