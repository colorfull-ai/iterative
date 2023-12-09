import os
import inspect
import yaml
from typing import List
from fastapi import APIRouter
from iterative.utils import load_module_from_path, find_iterative_root
from logging import getLogger

logger = getLogger(__name__)

def read_api_path_from_config(config_path: str) -> str:
    """
    Reads the API path from the project's configuration file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        str: The API path specified in the configuration.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        return config.get('api_generation_path', 'api')

def get_api_routers_from_path(api_path: str) -> List[APIRouter]:
    """
    Searches for FastAPI routers in the specified 'api' path.

    Args:
        api_path (str): The path to the 'api' directory.

    Returns:
        List[APIRouter]: A list of discovered FastAPI routers.
    """
    routers = []
    if os.path.exists(api_path):
        for root, dirs, files in os.walk(api_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    # print(f"Found router: {full_path}")
                    module = load_module_from_path(full_path)
                    for name, obj in inspect.getmembers(module):
                        if isinstance(obj, APIRouter):
                            routers.append(obj)
    return routers

def get_api_routers():
    """
    Finds all FastAPI routers in the project, including those in the 'apps' subdirectories.
    """
    iterative_root = find_iterative_root(os.getcwd())
    if not iterative_root:
        iterative_root = os.getcwd()
        logger.debug(f"Could not find iterative root. Using current working directory: {iterative_root}")

    routers = []
    for root, dirs, files in os.walk(iterative_root):
        if '.iterative' in dirs:
            config_path = os.path.join(root, '.iterative', 'config.yaml')
            api_path = read_api_path_from_config(config_path)
            full_api_path = os.path.join(root, api_path)
            if os.path.exists(full_api_path):
                routers.extend(get_api_routers_from_path(full_api_path))
    
    logger.debug(f"Total routers found: {len(routers)}")
    return routers

# # Example usage
# all_routers = find_all_api_routers()
