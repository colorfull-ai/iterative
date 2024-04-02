import os
import textwrap
import traceback
import types
from typing import Optional
from iterative import get_config
from iterative.service.project_management.service.project_utils import (
    find_pydantic_models_in_models_folders,
    get_project_root,
    resolve_project_folder_path,
)
import humps
from logging import getLogger as _getLogger

logger = _getLogger(__name__)


def _find_models(models_path):
    """
    Search for model class definitions in Python files within the models_path directory.
    Returns a list of dictionaries with details about each model found.
    Each dictionary contains the file path and the model name.
    """
    # {model_name: model_path}
    models_dict = find_pydantic_models_in_models_folders(models_path)
    return models_dict


def find_models_in_cwd():
    """
    Search for model class definitions in Python files within the current working directory.

    Returns:
        list: A list of dictionaries with details about each model found. Each dictionary contains the file path and the model name.
    """
    cwd = os.getcwd()
    return _find_models(cwd)


def find_models_in_config_path():
    """
    Search for model class definitions in Python files within the model_generation_path directory.

    Returns:
        list: A list of dictionaries with details about each model found. Each dictionary contains the file path and the model name.
    """
    config_path = get_config().get("model_generation_path")
    return _find_models(config_path)


def find_models_in_iterative_project():
    """
    Search for model class definitions in Python files within the iterative project directory.

    Returns:
        list: A list of dictionaries with details about each model found. Each dictionary contains the file path and the model name.

    Raises:
        ValueError: If no iterative project directory is found.
    """
    project_root = get_project_root()
    if project_root:
        return _find_models(project_root)
    else:
        raise ValueError("No .iterative project found in the current directory tree.")

