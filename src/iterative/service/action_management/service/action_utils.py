import os
import inspect
from typing import Callable, Dict, List
from fastapi import APIRouter
from fastapi.routing import APIRoute
from iterative import get_config
from iterative.service.project_management.models.project_models import ProjectFolder
from iterative.service.project_management.service.project_utils import (
    is_action_file,
    is_private_folder,
    is_template_folder,
    resolve_project_folder_path,
    get_project_root,
    load_module_from_path,
    is_iterative_project
)
from iterative.service.api_management.service.api_utils import (
    find_api_routers_in_iterative_project,
    find_api_routers_in_parent_project,
)
from iterative.service.action_management.models.action import Action
from logging import getLogger
from iterative.web_app_integration import integrate_actions_into_web_app


logger = getLogger(__name__)

def find_project_actions():
    return turn_dir_into_actions(resolve_project_folder_path(ProjectFolder.ACTIONS.value), "Project Actions")


def is_valid_python_file(file_name: str):
    """
    This function checks if a file is a valid Python file.
    """
    return file_name.endswith(".py")


def is_public_function(name: str):
    """
    This function checks if a function is public.
    """
    return not name.startswith("_")


def turn_function_into_action(name: str, func: Callable, file: str, script_source: str):
    """
    This function creates an Action from a function.
    """
    return Action(name=name, function=func, file_path=file, category=script_source)


def turn_python_file_into_actions(full_path: str, script_source: str):
    """
    This function processes a Python file and returns a list of Actions created from the functions in the file.
    """
    actions = []
    module = load_module_from_path(full_path)
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if is_public_function(name):
            action = turn_function_into_action(name, func, full_path, script_source)
            actions.append(action)
    return actions


def turn_dir_into_actions(directory: str, script_source: str):
    """
    This function processes the Python action files in a directory and returns a list of Actions created from the functions in the files.
    """
    actions = []
    if not os.path.exists(directory):
        return actions

    if is_private_folder(directory):
        return actions

    if is_template_folder(directory):
        return actions


    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs if not is_private_folder(d) and not is_template_folder(d)
        ]
        for file in files:
            if is_valid_python_file(file) and is_action_file(file):
                full_path = os.path.join(root, file)
                actions.extend(turn_python_file_into_actions(full_path, script_source))
    return actions


def turn_py_files_into_actions(file_list: List[str], script_source: str):
    """
    This function processes a list of Python files and returns a list of Actions created from the functions in the files.
    """
    actions = []
    for file in file_list:
        if is_valid_python_file(file):
            actions.extend(turn_python_file_into_actions(file, script_source))
    return actions


def find_default_actions():
    default_actions_directory = os.path.join(
        get_project_root(os.path.dirname(os.path.abspath(__file__))),
        ProjectFolder.ACTIONS.value,
    )

    return turn_dir_into_actions(default_actions_directory, "Iterative Defaults")


def get_all_actions(
    include_project_actions=True,
    include_package_default_actions=True,
    include_api_actions=True,
) -> Dict[str, Action]:
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
        actions.extend(find_project_actions())

    if include_package_default_actions:
        actions.extend(find_default_actions())

    if include_api_actions:
        actions.extend(turn_project_routers_into_actions())

    all_actions_dict = {}
    for action in actions:
        if action.name in all_actions_dict:
            continue
        all_actions_dict[action.name] = action

    return all_actions_dict


def turn_route_into_action(route: APIRoute):
    """
    This function creates an Action from a route.
    """
    action_name = route.name or route.path.replace("/", "_")
    action_function = route.endpoint
    action_file = inspect.getfile(route.endpoint)  # File where the function is defined
    action_script_source = "API"  # This is a placeholder

    action = Action(
        name=action_name,
        function=action_function,
        file_path=action_file,
        category=action_script_source,
    )
    return action


def turn_router_into_actions(router: APIRouter):
    """
    This function takes a router and returns a list of actions created from the routes in the router.
    """
    actions = []
    for route in router.routes:
        action = turn_route_into_action(route)
        actions.append(action)
    return actions


def turn_routers_into_actions(routers: List[APIRouter]):
    """ """
    actions = []
    for router in routers:
        actions.extend(turn_router_into_actions(router))

    return actions


def _turn_routers_dict_into_actions(routers_dict: Dict):
    """
    This function takes a function to get routers and turns the routes into actions.
    """
    actions = []
    for project_name, router_list in routers_dict.items():
        for router_dict in router_list:
            router = router_dict["router"]
            actions.extend(turn_router_into_actions(router))

    return actions


def turn_project_routers_into_actions(project_path: str = "."):
    """
    This function searches the api folder in the project for FastAPI routers and turns the routes into actions.
    """
    if project_path != ".":
        project_root = get_project_root(project_path)
        return _turn_routers_dict_into_actions(
            find_api_routers_in_iterative_project(project_root)
        )
    return _turn_routers_dict_into_actions(find_api_routers_in_iterative_project())


def turn_parent_routers_into_actions():
    """
    This function searches the api folder in the parent project for FastAPI routers and turns the routes into actions.
    """
    return _turn_routers_dict_into_actions(find_api_routers_in_parent_project())


def get_configured_actions():
    config = get_config()
    project_root = os.getcwd()
    if not is_iterative_project(project_root):
        logger.info("Not an iterative project")
        # only return the default actions
        actions =  get_all_actions(include_package_default_actions=True, include_api_actions=False, include_project_actions=False)
        return actions, actions
    ai_actions = get_all_actions(
        include_project_actions=config.get("expose_project_actions_to_ai"),
        include_package_default_actions=config.get("expose_default_actions_to_ai"),
        include_api_actions=config.get("expose_api_actions_to_ai")
    )

    cli_actions = get_all_actions(
        include_project_actions=config.get("expose_project_actions_to_cli"),
        include_package_default_actions=config.get("expose_default_actions_to_cli"),
        # The CLI will never support API actions since the CLI can only handle Scalar arguments
        include_api_actions=False 
    )

    return ai_actions, cli_actions


def get_actions():
    from fastapi import FastAPI
    dummy_app = FastAPI()
    exposed_ai_actions, cli_actions = get_configured_actions()

    integrate_actions_into_web_app(exposed_ai_actions.values(), dummy_app)

    if get_config().get("let_ai_use_apis"):
        # Add routers to the web app
        routers = find_api_routers_in_parent_project()
        for router in routers:
            dummy_app.include_router(router)

    openapi_schema = dummy_app.openapi()

    functions = []
    paths = openapi_schema.get('paths', {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if path == "/":
                continue
            # Create a function name based on path and method
            function_name = f"{path.replace('/', '')}"

            # Extract and format parameters
            parameters = details.get('parameters', [])
            formatted_parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            for param in parameters:
                param_name = param.get('name')
                param_type = param.get('schema', {}).get('type', 'string')
                param_description = param.get('description', '')
                formatted_parameters['properties'][param_name] = {
                    "type": param_type,
                    "description": param_description
                }
                if param.get('required', False):
                    formatted_parameters['required'].append(param_name)

            # Add function to the list
            function = {
                "type": "function",
                "function": {
                    "name": function_name,
                    "description": details.get('summary', 'No description available'),
                    "parameters": formatted_parameters
                }
            }
            functions.append(function)
            
    return functions