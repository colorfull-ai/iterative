import os
import inspect
import yaml
from typing import List
from fastapi import APIRouter
from iterative.service.utils.project_utils import load_module_from_path
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
        if config is None:
            return 'api'
        
        return config.get('api_generation_path', 'api')

def get_api_routers_from_path(api_path: str, file_name: str = None) -> List[APIRouter]:
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
                    if file_name and file != file_name:
                        continue
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
    iterative_root = os.getcwd()
    if not iterative_root:
        iterative_root = os.getcwd()

    routers = []
    for root, dirs, files in os.walk(iterative_root):
        if '.iterative' in dirs:
            config_path = os.path.join(root, '.iterative', 'config.yaml')
            if not os.path.exists(config_path):
                continue
            api_path = read_api_path_from_config(config_path)
            full_api_path = os.path.join(root, api_path)
            if os.path.exists(full_api_path):
                routers.extend(get_api_routers_from_path(full_api_path))
    
    return routers

def get_model_router(model_name: str) -> List[APIRouter]:
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
                for router in get_api_routers_from_path(full_api_path, target_file_name):
                    print(f"Found router: {router}")
                    return router