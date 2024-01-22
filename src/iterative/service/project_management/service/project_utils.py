import ast
import sys
import os
import importlib.util
from typing import Dict
from iterative.service.project_management.models.project_models import ProjectFile, Project
from pydantic import BaseModel
import yaml
from logging import getLogger

logger = getLogger(__name__)


def snake_case(s: str) -> str:
    return s.replace("-", "_").replace(" ", "_")

def load_module_from_path(path: str):
    # Derive a module name from the file path
    module_name = os.path.splitext(os.path.basename(path))[0]

    # Add the directory containing the module to sys.path
    module_dir = os.path.dirname(path)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_project_folder_path(folder_path: str, parent: bool = False, package: bool = False, *args):
    if folder_path.startswith('/'):
        return os.path.join(folder_path, *args)
    else:
        if parent:
            return os.path.join(get_parent_project_root(), folder_path, *args)
        else:
            if package:
                return get_project_root(os.path.dirname(os.path.abspath(__file__)))
            project_root = get_project_root()
            if not project_root:
                return os.path.join(folder_path, *args)
            return os.path.join(get_project_root(), folder_path, *args)
    

def is_iterative_project(folder_path):
    if 'templates' in folder_path.split(os.sep):
        return False
    # Ensure the .iterative folder exists
    return os.path.exists(os.path.join(folder_path, ".iterative"))

def get_project_root(start_path: str = None):
    """
    This function returns the parent directory of the nearest `.iterative` folder. 
    It starts from the provided start_path or the current working directory and moves upwards in the directory tree. 

    The function works as follows:
    1. It gets the start_path or the current working directory.
    2. It enters a loop that continues until the root directory ('/') is reached.
    3. In each iteration of the loop, it checks if a `.iterative` folder exists in the current directory.
    4. If such a folder is found, it returns the current directory, which is the parent directory of the `.iterative` folder.
    5. If no `.iterative` folder is found in the current directory, it moves one level up in the directory tree.
    6. If the function reaches the root directory without finding a `.iterative` folder, it returns None.

    Args:
        start_path (str, optional): The path to start searching from. If not provided, the search starts from the current working directory.

    Returns:
        str: The path to the parent directory of the nearest `.iterative` folder, or None if no such folder is found.
    """
    path = start_path if start_path else os.getcwd()
    while path != '/':
        if os.path.exists(os.path.join(path, ".iterative")):
            return path
        path = os.path.dirname(path)
    logger.info("No '.iterative' project found.")
    return None


def find_all_iterative_projects(start_path):
    iterative_projects = []
    for root, dirs, files in os.walk(start_path):
        if '.iterative' in dirs:
            iterative_projects.append(root)
    return iterative_projects


def get_parent_project_root():
    """
    This function returns the greatest parent directory `iterative` project.
    It starts from the current working directory and moves upwards.

    The function works as follows:
    1. It gets the current working directory.
    2. It enters a loop that continues until the root directory ('/') is reached.
    3. In each iteration of the loop, it checks if a `.iterative` folder exists in the current directory.
    4. If such a folder is found, it stores the current directory, which is the parent directory of the `.iterative` folder.
    5. If no `.iterative` folder is found in the current directory, it moves one level up in the directory tree.
    6. If the function reaches the root directory, it returns the last stored directory, or None if no `.iterative` folder was found.

    Returns:
        str: The path to the parent directory of the last `.iterative` folder found, or None if no such folder is found.
    """
    path = os.getcwd()
    last_project_root = None
    while True:
        if os.path.exists(os.path.join(path, ".iterative")):
            last_project_root = path
        parent_path = os.path.dirname(path)
        if path == parent_path:  # We've reached the root directory
            break
        path = parent_path
    return last_project_root


def is_pydantic_model(node, file_path):

    # Get the root directory of the project
    project_root = os.path.dirname(file_path)

    # Add the project root to sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Dynamically import the module
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # Get the class from the module
    model_class = getattr(module, node.name, None)

    # Check if it's a subclass of BaseModel
    if model_class and issubclass(model_class, BaseModel):
        return True

    return False

def find_pydantic_models_in_models_folders(root_path) -> Dict[str, str]:
    models = {}
    for root, dirs, files in os.walk(root_path):
        if 'models' in root.split(os.sep):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        try:
                            tree = ast.parse(file_content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef) and is_pydantic_model(node, file_path):
                                    # Include both file name and class name in the model identifier
                                    model_identifier = f"{file.split('.')[0]}.{node.name}"
                                    models[model_identifier] = file_path
                        except SyntaxError:
                            continue
    models = dict(sorted(models.items()))
    return models

def read_project_config_file(project_root: str):
    """
    This function reads the configuration file from the given project root and returns it.
    """
    config_file_path = os.path.join(project_root, ".iterative", "config.yaml")

    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)


    return config

def get_project_config(project_path: str = None):
    """
    This function reads the project configuration from the 'iterative.yml' file and returns it.
    """
    project_root = get_project_root(project_path)
    return read_project_config_file(project_root)

def get_current_project_config():
    """
    This function reads the configuration of the current project and returns it.
    """
    project_root = get_project_root()
    return read_project_config_file(project_root)

def get_parent_project_config():
    """
    This function reads the configuration of the parent project and returns it.
    """
    project_root = get_parent_project_root()
    return read_project_config_file(project_root)

def is_private_folder(folder_name: str) -> bool:
    """
    This function checks if a folder is private, i.e., if it is prefixed with a "." or "_".
    """
    return folder_name.startswith('.') or folder_name.startswith('_')

def is_template_folder(folder_name: str) -> bool:
    """
    This function checks if a folder is a template folder, i.e., if it is prefixed with a "." or "_".
    """
    return folder_name.startswith('templates')

def is_action_file(file_name: str) -> bool:
    """
    This function checks if a file is an action file, i.e., if it is prefixed with a "." or "_".
    """
    return file_name.endswith(ProjectFile.ACTION_POSTFIX.value)

def get_project_name(project_path: str = None):
    """
    This function returns the name of the project.
    """
    project_root = get_project_root(project_path)
    if project_root is None:
        return None
    return os.path.basename(project_root)

def create_project_instance(project_path: str):
    """
    Create a Project instance from the given project path.

    Args:
        project_path (str): The path to the project.

    Returns:
        Project: The created Project instance.
    """
    project_root = get_project_root(project_path)
    if project_root is None:
        logger.warning(f"No project found at {project_path}.")
        return None

    # Read the project configuration
    config = get_project_config(project_root)

    # Find all Pydantic models in the project
    models = find_pydantic_models_in_models_folders(project_root)

    # TODO: Add code to read other necessary data (e.g., services, actions)

    # Create the Project instance
    project = Project(
        root_path=project_root,
        config=config,
        models=models,
        # TODO: Add other necessary data (e.g., services, actions)
    )

    return project

