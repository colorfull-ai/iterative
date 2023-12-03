from nosql_yorm.cache import cache_handler
from iterative.config import get_config
import os

data_path = os.path.join(os.getcwd(), get_config().get("data_path"))


cache_handler.set_output_dir(data_path)
cache = cache_handler