import os
from iterative.models.config import IterativeAppConfig
from omegaconf import OmegaConf
from nosql_yorm.config import Config as NosqlYormConfig, set_config as set_nosql_yorm_config
from pydantic import ValidationError
from logging import getLogger

logger = getLogger(__name__)


class Config:
    def __init__(self,  merge_config=True):
        user_config_path = self.find_iterative_config()
        default_config = OmegaConf.create(IterativeAppConfig().dict())
        nosql_yorm_config = NosqlYormConfig()

        # Load and validate the user configuration if provided
        if user_config_path and os.path.exists(user_config_path):
            user_config = OmegaConf.merge(nosql_yorm_config.config,  default_config,  OmegaConf.load(user_config_path))


        else:
            user_config = OmegaConf.merge(nosql_yorm_config.config, default_config)

        try:
            self.config = OmegaConf.create(IterativeAppConfig(**OmegaConf.to_object(user_config)).dict())
        except ValidationError as e:
            print(f"Validation error in the user configuration: {e}")
            raise

        # Set the merged configuration as the nosql_yorm configuration
        set_nosql_yorm_config(self)

        
    def find_iterative_config(self):
        current_dir = os.getcwd()
        while True:
            possible_config_path = os.path.join(current_dir, ".iterative", 'config.yaml')
            if os.path.exists(possible_config_path):
                logger.debug(f"Found iterative project")
                return possible_config_path
            new_dir = os.path.dirname(current_dir)
            if new_dir == current_dir:
                # Root directory reached without finding the config file
                return None
            current_dir = new_dir

    def get(self, key, default=None):
        if not key:
            return default
        value = self.config.get(key, default)
        return value

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
    
    def set(self, key, value):
        """
        Set a configuration value.

        Args:
            key (str): The configuration key to set.
            value: The value to set for the key.
        """
        if key not in self.config:
            raise KeyError(f"Config key {key} does not exist")

        # Update the configuration
        OmegaConf.update(self.config, key, value, merge=False)

        # If there are any additional actions needed after updating the config,
        # such as revalidating the configuration or updating external systems,
        # include them here.
        try:
            validated_config = IterativeAppConfig(**OmegaConf.to_object(self.config))
            self.config = OmegaConf.create(validated_config.dict())
        except ValidationError as e:
            print(f"Validation error after updating the configuration: {e}")
            raise

        # Update the nosql_yorm configuration if necessary
        set_nosql_yorm_config(self)


# Global shared configuration instance
_shared_config = Config()

def set_config(config):
    global _shared_config
    _shared_config = config

def get_config():
    global _shared_config
    return _shared_config
