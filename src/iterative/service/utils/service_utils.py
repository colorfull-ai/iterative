from collections import defaultdict
import os
import ast

from iterative.models.project_folder import ProjectFolder
from iterative.service.utils.project_utils import get_parent_project_root, get_project_root, is_iterative_project
import yaml

def find_project_service_functions(service_path):
    """
    Recursively search for function definitions in Python files within the service_path directory
    and any nested service directories specified in the '.iterative/config.yaml' file.
    Returns a dictionary with details about each function found.
    Each key-value pair in the dictionary is the function name and the file path.
    """
    functions_dict = defaultdict(list)

    def add_functions_from_path(search_path):
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    project_name = os.path.basename(root)

                    module = ast.parse(file_content)
                    functions = [node.name for node in ast.walk(module) if isinstance(node, ast.FunctionDef)]
                    for function in functions:
                        functions_dict[project_name].append({
                            "file_path": file_path,
                            "project_name": project_name,
                            "func": function,
                            "function_name": function,
                        })

    # Check if the provided service path is part of an iterative project
    if is_iterative_project(service_path):
        config_path = os.path.join(service_path, '.iterative', 'config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            nested_service_paths = config.get('service_generation_paths', [ProjectFolder.SERVICE.value])
            for nested_service_path in nested_service_paths:
                full_nested_path = os.path.join(service_path, nested_service_path)
                add_functions_from_path(full_nested_path)
        else:
            print(f"No config.yaml found in {service_path}. Using default service path.")
            add_functions_from_path(service_path)
    else:
        print(f"{service_path} is not an iterative project. Using default service path.")
        add_functions_from_path(service_path)

    return functions_dict


def find_project_service_functions_in_iterative_project():
    project_root = get_project_root()
    if project_root:
        return find_project_service_functions(project_root)
    else:
        print("No .iterative project found in the current directory tree.")
        return {}
    
def find_project_service_functions_in_parent_project():
    parent_project_root = get_parent_project_root()
    if parent_project_root:
        return find_project_service_functions(parent_project_root)
    else:
        print("No .iterative project found in the current directory tree.")
        return {}
