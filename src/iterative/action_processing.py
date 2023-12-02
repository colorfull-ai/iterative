import os
import inspect
from iterative.cli import find_iterative_root
from iterative.config import get_config
from iterative.models.action import Action
from iterative.utils import load_module_from_path

def get_project_actions():
    iterative_root = find_iterative_root(os.getcwd())
    user_actions_path = get_config().get("actions_search_path", "actions")

    actions = []

    if not get_config().get("discover_actions"):
        print("Action discovery is disabled. Exiting discovery process.")
        return actions

    if iterative_root:
        print(f"Iterative Project Found at {iterative_root}.")
        print(f"Searching for actions in {user_actions_path}...")

        iterative_actions_directory = os.path.join(iterative_root, user_actions_path)
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

                    # Create an Action instance using keyword arguments
                    action = Action(name=name, function=func, file=file, script_source=script_source)
                    actions.append(action)
    return actions

def get_package_default_actions():
    default_actions_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions")
    
    print(f"Processing default actions in {default_actions_directory}")
    return process_python_action_files(default_actions_directory, "Package Default")

def get_all_actions():
    project_actions = get_project_actions()
    package_default_actions = get_package_default_actions()

    all_actions_dict = {}
    for action in project_actions + package_default_actions:
        if action.name in all_actions_dict:
            raise ValueError(f"Duplicate action found: {action.name}")
        all_actions_dict[action.name] = action

    return all_actions_dict
