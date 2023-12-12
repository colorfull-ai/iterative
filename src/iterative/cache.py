from iterative.utils import create_project_path
from nosql_yorm.cache import cache_handler
from iterative.config import get_config

data_path = create_project_path(get_config().get("data_path"))

cache_handler.set_output_dir(data_path)
cache = cache_handler