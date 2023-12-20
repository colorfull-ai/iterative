import os
import ast
import textwrap

from iterative import get_config
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
    functions_dict = {}

    def add_functions_from_path(search_path):
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    module = ast.parse(file_content)
                    functions = [node.name for node in ast.walk(module) if isinstance(node, ast.FunctionDef)]
                    for function in functions:
                        functions_dict[function] = file_path

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

def find_project_service_functions_in_config_path():
    config_path = get_config().get('service_generation_path')
    return find_project_service_functions(config_path)


def find_project_service_functions_in_cwd():
    cwd = os.getcwd()
    return find_project_service_functions(cwd)


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


def read_function_file(function_name: str):
    functions = find_project_service_functions_in_config_path()
    function_path = functions[function_name]
    with open(function_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    return file_content

def overwrite_function_in_file(function_name: str, new_function_code: str):
    functions = find_project_service_functions_in_config_path()
    function_path = functions[function_name]

    # Read the original file content
    with open(function_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Parse the file content into an AST
    module = ast.parse(file_content)

    # Find the function to overwrite and replace its body
    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            new_function_body = ast.parse(textwrap.dedent(new_function_code)).body
            node.body = new_function_body

    # Convert the modified AST back into code
    new_file_content = compile(module, filename="<ast>", mode="exec")

    # Create an isolated scope for the exec function
    isolated_scope = {}

    # Try to execute the new code to check if it's valid
    try:
        exec(new_file_content, isolated_scope)
    except Exception as e:
        raise ValueError(f"Failed to execute the new function code: {e}")

    # If the new code is valid, overwrite the original file
    with open(function_path, 'w', encoding='utf-8') as f:
        f.write(new_file_content)

    return True