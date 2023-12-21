from collections import defaultdict
import os
import inspect
from aiohttp_retry import Dict
import yaml
from fastapi import APIRouter
from iterative.service.utils.project_utils import get_parent_project_root, get_project_root, is_iterative_project, load_module_from_path
from logging import getLogger

logger = getLogger(__name__)

def read_api_path_from_config(config_path: str) -> str:
    """
    Reads the API path from the project's configuration file.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        return config.get('api_generation_path', 'api') if config else 'api'

def find_api_routers_from_path(start_path: str, file_name: str = None):
    """
    Searches for FastAPI routers in the specified start path and its 'service' directories.
    Checks the start path for an 'api' directory and then recursively searches in 'service' directories.
    Only considers directories that are identified as iterative projects.
    """
    routers_dict = defaultdict(list)

    def add_routers_from_path(search_path):
        for root, _, files in os.walk(search_path):
            for file in files:
                if file.endswith(".py") and (not file_name or file == file_name):
                    full_path = os.path.join(root, file)
                    module = load_module_from_path(full_path)
                    project_path = get_project_root(root)
                    project_name = os.path.basename(project_path)

                    for _, obj in inspect.getmembers(module):
                        if isinstance(obj, APIRouter):
                            routers_dict[project_name].append({
                                "file_path": full_path,
                                "project_name": project_name,
                                "router": obj,
                                "router_name": "Unnamed router"
                            })

    def search_iterative_projects_in_service_dirs(root_path):
        if is_iterative_project(root_path):
            api_folder = os.path.join(root_path, 'api')
            if os.path.exists(api_folder):
                add_routers_from_path(api_folder)

        for root, dirs, _ in os.walk(root_path):
            if 'service' in root.split(os.sep):  # Checking if 'service' is in the path
                for dir in dirs:
                    service_dir_path = os.path.join(root, dir)
                    if is_iterative_project(service_dir_path):
                        api_folder = os.path.join(service_dir_path, 'api')
                        if os.path.exists(api_folder):
                            add_routers_from_path(api_folder)

    search_iterative_projects_in_service_dirs(start_path)
    return routers_dict


def get_api_routers():
    """
    Finds all FastAPI routers in the project, including those in the 'apps' subdirectories.
    """
    routers = find_api_routers_in_parent_project()
    return routers


def find_api_routers_in_iterative_project():
    project_root = get_project_root()
    if project_root:
        return find_api_routers_from_path(project_root)
    else:
        print("No .iterative project found in the current directory tree.")
        return {}
    

def find_api_routers_in_parent_project():
    parent_project_root = get_parent_project_root()
    print(f"Parent project root: {parent_project_root}")
    if parent_project_root:
        return find_api_routers_from_path(parent_project_root)
    else:
        print("No .iterative project found in the current directory tree.")
        return {}


def get_model_router(model_name: str):
    """
    Finds FastAPI routers in the project, filtering by a specified model name.

    Args:
        model_name (str): The name of the model to find the router for.

    Returns:
        List[APIRouter]: A list of FastAPI routers related to the specified model.
    """
    iterative_root = os.getcwd()
    target_file_name = f"{model_name.lower()}_api.py"  # File name pattern

    for root, dirs, _ in os.walk(iterative_root):
        if '.iterative' in dirs:
            config_path = os.path.join(root, '.iterative', 'config.yaml')
            if not os.path.exists(config_path):
                continue

            api_path = read_api_path_from_config(config_path)
            full_api_path = os.path.join(root, api_path)
            if os.path.exists(full_api_path):
                # Filter routers by the target file name
                for router in find_api_routers_from_path(full_api_path, target_file_name):
                    print(f"Found router: {router}")
                    return router