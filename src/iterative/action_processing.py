import os
import inspect
from iterative.cli import find_iterative_root
from iterative.config import get_config
from iterative.utils import load_module_from_path
from iterative.cli_app_integration import integrate_actions_into_cli_app
from iterative.web_app_integration import integrate_actions_into_web_app, load_routers_from_directory

def get_project_actions():
    iterative_root = find_iterative_root(os.getcwd())
    user_actions_path = get_config().get("actions", "actions_search_path")

    actions = []

    if not get_config().get("discover_actions"):
        print("Action discovery is disabled. Exiting discovery process.")
        return actions

    if iterative_root:
        print(f"Iterative Project Found at {iterative_root}.")
        actions_folder = get_config().get(user_actions_path, "actions")
        print(f"Searching for actions in {actions_folder}...")

        iterative_actions_directory = os.path.join(iterative_root, actions_folder)
        actions.extend(process_python_action_files(iterative_actions_directory, "User Script"))

    return actions

def process_python_action_files(directory, script_source):
    actions = []
    if not os.path.exists(directory):
        print(f"'actions' directory not found in {directory}")
        return actions

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                module = load_module_from_path(full_path)
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith('_'):
                        continue

                    action = {
                        "name": name,
                        "function": func,
                        "file": file,
                        "script_source": script_source
                    }
                    actions.append(action)
    return actions

def get_package_default_actions():
    # Define the path to the directory containing the default actions
    default_actions_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    
    print(f"Processing default actions in {default_actions_directory}")
    return process_python_action_files(default_actions_directory, "Package Default")


def get_all_actions():
    project_actions = get_project_actions()
    package_default_actions = get_package_default_actions()

    # Combine project actions with package default actions
    all_actions = project_actions + package_default_actions
    return all_actions


def find_and_process_package_actions(cli_app, web_app):
    print("Searching for package actions...")
    # Process default actions
    default_actions_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    print(f"Processing default actions in {default_actions_directory}")

    process_actions_directory(default_actions_directory, cli_app, web_app, script_source="Iterative Default")

def process_python_action_files(directory, script_source):
    actions = []
    if not os.path.exists(directory):
        print(f"'actions' directory not found in {directory}")
        return actions

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                module = load_module_from_path(full_path)
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith('_'):
                        continue

                    action = {
                        "name": name,
                        "function": func,
                        "file": file,
                        "script_source": script_source
                    }
                    actions.append(action)
    return actions
