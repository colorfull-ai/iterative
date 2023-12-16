from iterative.service.utils.project_utils import create_project_path
from nosql_yorm import cache as nosql_cache
from iterative.config import get_config

data_path = create_project_path(get_config().get("data_path"))

nosql_cache.set_output_dir(data_path)
cache = nosql_cache