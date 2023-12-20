import ast
import os
import textwrap
import traceback
import types
from iterative import get_config as _get_config
from iterative.service.utils.project_utils import find_pydantic_models_in_models_folders, get_project_root

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
    cwd = os.getcwd()
    return _find_models(cwd)

def find_models_in_config_path():
    config_path = _get_config().get('model_generation_path')
    return _find_models(config_path)

def find_models_in_iterative_project():
    project_root = get_project_root()
    if project_root:
        return _find_models(project_root)
    else:
        print("No .iterative project found in the current directory tree.")
        return []

def read_model_file(model_path: str):
    with open(model_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    return file_content

def read_model_file(model_name: str):
    models = find_models_in_config_path()
    model_path = models[model_name]
    with open(model_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    return file_content

def overwrite_model_file(model_name: str, new_file_content: str):
    models = find_models_in_config_path()
    model_path = models[model_name]
    with open(model_path, 'w', encoding='utf-8') as f:
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