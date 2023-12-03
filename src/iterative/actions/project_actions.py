import inspect
import json
import os
from typing import List
from fastapi import APIRouter
from iterative import get_config as _get_config
from iterative.models.config import IterativeAppConfig
from iterative.utils import find_iterative_root, load_module_from_path

def create_folders(path: str):
    """
    Creates all folders needed for a given path if they don't exist.

    Args:
        path (str): The path of the directory to be created. This can be an absolute or relative path.

    Returns:
        None
    """
    if not os.path.exists(path):
        os.makedirs(path)

def create_actions_directory():
    """
    Creates a directory for actions if it doesn't exist.
    """
    actions_directory = os.path.join(_get_config().get("actions_search_path"))
    create_folders(actions_directory)

def create_services_directory():
    """
    Creates a directory for services if it doesn't exist.
    """
    services_directory = os.path.join(_get_config().get("services_generation_path"))
    create_folders(services_directory)

def create_data_directory():
    """
    Creates a directory for data if it doesn't exist.
    """
    data_directory = os.path.join(_get_config().get("data_path"))
    create_folders(data_directory)

def create_logs_directory():
    """
    Creates a directory for logs if it doesn't exist.
    """
    logs_directory = os.path.join(_get_config().get("logs_path"))
    create_folders(logs_directory)

def create_tests_directory():
    """
    Creates a directory for tests if it doesn't exist.
    """
    tests_directory = os.path.join(_get_config().get("tests_path"))
    create_folders(tests_directory)

def get_project_config():
    """
    Returns the project configuration.
    """

    return _get_config()

def get_config_schema():
    """
    Returns the schema for the project configuration.
    """

    print(IterativeAppConfig.schema())
    return IterativeAppConfig.schema()

def set_config_value(key: str, value: str):
    f"""
    Sets a configuration value.

    Schema:
    {json.dumps(get_config_schema(), indent=2)}
    """

    _get_config()[key] = value
