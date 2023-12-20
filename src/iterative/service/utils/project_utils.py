import ast
import sys
import os
import importlib.util
from typing import Dict
from pydantic import BaseModel


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

        
def print_iterative():
    ascii_art = """
                                 ___           ___           ___                                                    ___     
       ___         ___          /  /\         /  /\         /  /\          ___            ___         ___          /  /\    
      /__/\       /__/\        /  /::\       /  /::\       /  /::\        /__/\          /__/\       /  /\        /  /::\   
      \__\:\      \  \:\      /  /:/\:\     /  /:/\:\     /  /:/\:\       \  \:\         \__\:\     /  /:/       /  /:/\:\  
      /  /::\      \__\:\    /  /::\ \:\   /  /::\ \:\   /  /::\ \:\       \__\:\        /  /::\   /  /:/       /  /::\ \:\ 
   __/  /:/\/      /  /::\  /__/:/\:\ \:\ /__/:/\:\_\:\ /__/:/\:\_\:\      /  /::\    __/  /:/\/  /__/:/  ___  /__/:/\:\ \:\
  /__/\/:/~~      /  /:/\:\ \  \:\ \:\_\/ \__\/~|::\/:/ \__\/  \:\/:/     /  /:/\:\  /__/\/:/~~   |  |:| /  /\ \  \:\ \:\_\/
  \  \::/        /  /:/__\/  \  \:\ \:\      |  |:|::/       \__\::/     /  /:/__\/  \  \::/      |  |:|/  /:/  \  \:\ \:\  
   \  \:\       /__/:/        \  \:\_\/      |  |:|\/        /  /:/     /__/:/        \  \:\      |__|:|__/:/    \  \:\_\/  
    \__\/       \__\/          \  \:\        |__|:|~        /__/:/      \__\/          \__\/       \__\::::/      \  \:\    
                                \__\/         \__\|         \__\/                                      ~~~~        \__\/    
    """
    print(ascii_art + " : By Colorfull")


def create_project_path(folder_path, *args):
    if folder_path.startswith('/'):
        return os.path.join(folder_path, *args)
    else:
        return os.path.join(os.getcwd(), folder_path, *args)
    

def is_cwd_iterative_project():
    # Ensure the .iterative folder exists
    return os.path.exists(os.path.join(os.getcwd(), ".iterative"))

def get_project_root():
    """
    This function returns the parent directory of the nearest `.iterative` folder. 
    It starts from the current working directory and moves upwards in the directory tree. 

    The function works as follows:
    1. It gets the current working directory.
    2. It enters a loop that continues until the root directory ('/') is reached.
    3. In each iteration of the loop, it checks if a `.iterative` folder exists in the current directory.
    4. If such a folder is found, it returns the current directory, which is the parent directory of the `.iterative` folder.
    5. If no `.iterative` folder is found in the current directory, it moves one level up in the directory tree.
    6. If the function reaches the root directory without finding a `.iterative` folder, it returns None.

    Returns:
        str: The path to the parent directory of the nearest `.iterative` folder, or None if no such folder is found.
    """
    path = os.getcwd()
    while path != '/':
        if os.path.exists(os.path.join(path, ".iterative")):
            return path
        path = os.path.dirname(path)
    return None


def find_all_iterative_projects(start_path):
    iterative_projects = []
    for root, dirs, files in os.walk(start_path):
        if '.iterative' in dirs:
            iterative_projects.append(root)
    return iterative_projects

def get_last_project_root():
    """
    This function returns the parent directory of the last `.iterative` folder found while moving up the directory tree. 
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
    while path != '/':
        if os.path.exists(os.path.join(path, ".iterative")):
            last_project_root = path
        path = os.path.dirname(path)
    return last_project_root


def is_pydantic_model(node, file_path):
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