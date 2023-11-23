import logging
import colorlog
from .config import _shared_config

def get_logger(name):
    logging_config = _shared_config.get("logging")
    formatter = colorlog.ColoredFormatter(
        f"%(asctime)s - %(log_color)s{name}%(reset)s - "
        f"%(log_color)s%(levelname)s%(reset)s - %(message_log_color)s%(message)s%(reset)s",
        datefmt=logging_config["date_format"],
        log_colors=logging_config["log_colors"],
        secondary_log_colors={
            'message': logging_config["secondary_log_colors"]["message"]
        }
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger
