import os
import inspect
from typing import Dict
from iterative.api_processing import get_api_routers
from iterative.config import get_config
from iterative.models.action import Action
from iterative.service.utils.project_utils import load_module_from_path
from logging import getLogger

logger = getLogger(__name__)

def get_project_actions():
    iterative_root = os.getcwd()
    user_actions_path = get_config().get("actions_search_path", "actions")

    actions = []

    if iterative_root:
        iterative_actions_directory = os.path.join(iterative_root, user_actions_path)
        actions.extend(process_python_action_files(iterative_actions_directory, "User Script"))

    return actions

def process_python_action_files(directory, script_source):
    actions = []
    if not os.path.exists(directory):
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
    
    return process_python_action_files(default_actions_directory, "Package Default")

def get_all_actions(include_project_actions=True, include_package_default_actions=True, include_api_actions=True) -> Dict[str, Action]:
    """
    Get all actions, with options to include or exclude project actions and package default actions.

    Args:
    include_project_actions (bool): Flag to include project actions. Defaults to True.
    include_package_default_actions (bool): Flag to include package default actions. Defaults to True.

    Returns:
    Dict[str, Action]: Dictionary of actions keyed by action name.
    """
    actions = []

    if include_project_actions:
        actions.extend(get_project_actions())

    if include_package_default_actions:
        actions.extend(get_package_default_actions())

    if include_api_actions:
        actions.extend(get_api_actions())

    all_actions_dict = {}
    for action in actions:
        if action.name in all_actions_dict:
            continue
        all_actions_dict[action.name] = action

    return all_actions_dict


def get_api_actions():
    """
    This searches the api folder in the project for FastAPI routers and turns the routes into actions.
    """
    actions = []
    for router in get_api_routers():
        for route in router.routes:
            # Example of creating an Action from a route
            # You may need to adjust this according to your route structure and requirements
            action_name = route.name or route.path.replace('/', '_')
            action_function = route.endpoint
            action_file = inspect.getfile(route.endpoint)  # File where the function is defined
            action_script_source = "API"  # This is a placeholder

            action = Action(
                name=action_name,
                function=action_function,
                file=action_file,
                script_source=action_script_source
            )
            actions.append(action)

            # Optional print for debugging

    return actions