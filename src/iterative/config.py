from omegaconf import OmegaConf
import os

class Config:
    def __init__(self, user_config_path=None, merge_config=True):
        self.default_config = OmegaConf.create()
        default_config_path = os.path.join(os.path.dirname(__file__), 'default_config.yaml')

        if os.path.exists(default_config_path):
            self.default_config = OmegaConf.load(default_config_path)
        elif merge_config:
            raise ValueError("Default configuration file not found.")

        self.user_config = OmegaConf.load(user_config_path) if user_config_path and os.path.exists(user_config_path) else OmegaConf.create()

        if merge_config:
            # Merge user config with default config
            self.config = OmegaConf.merge(self.default_config, self.user_config)
        else:
            # Use only the user config, disregarding the default config
            self.config = self.user_config

    def get(self, key, default=None):
        return self.config.get(key, default)

# Global shared configuration instance
_shared_config = Config()

def set_global_config(config):
    global _shared_config
    _shared_config = config

def _get_global_config():
    global _shared_config
    return _shared_config