import os
import inspect
from typing import List
from fastapi import APIRouter
from iterative.config import get_config
from iterative.utils import load_module_from_path, find_iterative_root
from logging import getLogger

logger = getLogger(__name__)

def get_api_routers():
    """
    This searches the api folder in the project for fastapi routers and 
    """
    api_path = get_config().get("api_search_path", "api")
    iterative_root = find_iterative_root(os.getcwd())
    if not iterative_root:
        iterative_root = os.getcwd()
        logger.debug(f"Could not find iterative root. Using current working directory: {iterative_root}")
        
    api_directory = os.path.join(iterative_root, api_path)

    routers: List[APIRouter] = []
    if os.path.exists(api_directory):
        for root, dirs, files in os.walk(api_directory):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    module = load_module_from_path(full_path)
                    for name, obj in inspect.getmembers(module):
                        if isinstance(obj, APIRouter):
                            routers.append(obj)

    logger.debug(f"Found {len(routers)} routers in {api_directory}")

    return routers
