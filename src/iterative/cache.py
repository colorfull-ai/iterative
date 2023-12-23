from iterative.service.utils.project_utils import resolve_project_folder_path
from iterative.models.project_folder import ProjectFolder
from nosql_yorm import cache as nosql_cache

data_path = resolve_project_folder_path(ProjectFolder.DATA.value)

nosql_cache.set_output_dir(data_path)
cache = nosql_cache