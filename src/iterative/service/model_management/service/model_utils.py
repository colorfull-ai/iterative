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


def read_model_file(model_name: str) -> str:
    """
    Reads the contents of a model file.

    Args:
        model_name (str): The name of the model file to read.

    Returns:
        str: The contents of the model file.
    """
    models = find_models_in_config_path()
    model_path = models[model_name]
    with open(model_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    return file_content


def overwrite_model_file(model_name: str, new_file_content: str):
    """
    Overwrite the contents of a model file with the given new content.

    Args:
        model_name (str): The name of the model file to overwrite.
        new_file_content (str): The new content to write to the model file.

    Returns:
        bool: True if the file was successfully overwritten, False otherwise.
    """
    models = find_models_in_config_path()
    model_path = models[model_name]
    with open(model_path, "w", encoding="utf-8") as f:
        f.write(new_file_content)
    return True


def execute_python_code_isolated(code: str, **kwargs):
    """
    Execute Python code in an isolated environment.
    """
    # Create a temporary module
    module_name = "tmp_module"
    module = types.ModuleType(module_name)
    module.__dict__.update(kwargs)

    try:
        # Execute the code in the temporary module
        exec(textwrap.dedent(code), module.__dict__)
    except Exception as e:
        # Catch the exception and return its traceback
        return traceback.format_exc()

    # Return the temporary module
    return module


def create_model_content(entity_name: str):
    """
    Create a basic nosql_yorm model content with the given entity name.
    """
    # Generate class name in pascal case
    class_name = humps.pascalize(entity_name)

    model_content = textwrap.dedent(
        f"""\
    from iterative import IterativeModel
    from typing import *
    from iterative.models import * 

    class {class_name}(IterativeModel):
        _collection_name = "{class_name}"
        # TODO: Add fields here
    """
    )

    return model_content, class_name


def write_model_file(entity_name: str, model_generation_path: Optional[str] = None):
    """
    Write a basic nosql_yorm model file with the given entity name in a 'models' directory.
    Also updates __init__.py to import the new model and add it to the __all__ list.
    """
    # Fetch the model generation path from the global configuration if not provided
    if not model_generation_path:
        model_generation_path = get_config().get("model_generation_path")

    # Append 'models' to the model generation path to ensure the directory structure
    model_folder = resolve_project_folder_path(model_generation_path)

    # Create the models directory if it doesn't exist
    try:
        os.makedirs(model_folder, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating directory {model_folder}: {e}")
        return

    # Generate file name in snake case
    file_name = humps.decamelize(entity_name) + ".py"

    file_path = os.path.join(model_folder, file_name)
    model_content, class_name = create_model_content(entity_name)

    # Write the model class to the file
    with open(file_path, "w") as file:
        file.write(model_content)

    logger.info(f"Model {class_name} created at {file_path}")
    return model_content
