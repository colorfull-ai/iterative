from functools import wraps
import os
from fastapi import APIRouter, FastAPI, HTTPException
from typing import Callable, List, get_type_hints
import inspect
from iterative.service.action_management.models.action import Action
from iterative.service.api_management.service.api_utils import find_api_routers_in_parent_project
from iterative.service.project_management.service.project_utils import load_module_from_path, snake_case
from logging import getLogger

logger = getLogger(__name__)

def create_endpoint(func: Callable, name: str):
    router = APIRouter()

    # Retrieve the original function if it's wrapped
    original_func = getattr(func, "__wrapped__", func)

    # Extract type hints and docstring from the original function
    type_hints = get_type_hints(original_func)
    response_model = type_hints.get('return')

    # Create a dynamic function with the same signature as the original function
    sig = inspect.signature(original_func)
    params = sig.parameters

    @wraps(original_func)
    async def endpoint(*args, **kwargs):
        try:
            result = original_func(*args, **kwargs)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Set the dynamically constructed signature to the endpoint function
    endpoint.__signature__ = sig.replace(return_annotation=response_model)

    # Add docstring and annotations as route description and response model
    endpoint.__doc__ = original_func.__doc__
    router.add_api_route(
        f"/{name}", 
        endpoint, 
        methods=["GET"],  # Adjust based on your function's method
        response_model=response_model
    )

    return router

def load_routers_from_directory(directory, web_app):
    # Skip if the directory doesn't exist
    if not os.path.exists(directory):
        logger.info(f"Directory not found: {directory}")
        return

    # Search for Python actions in the provided directory and load routers
    for file in os.listdir(directory):
        if file.endswith(".py") and not file.startswith("_"):
            full_path = os.path.join(directory, file)
            module_name = os.path.splitext(file)[0]
            module = load_module_from_path(full_path)

            # Assuming each script has a router named 'router'
            if hasattr(module, "router"):
                web_app.include_router(module.router)

def integrate_actions_into_web_app(actions: List[Action], web_app: FastAPI):
    for action in actions:
        snake_name = snake_case(action.get_name())
        router = create_endpoint(action.get_function(), snake_name)
        category = action.get_category()
        file = action.get_file()

        # Determine tags based on script source
        tag = [f"{category}: {file.replace('.py', '')}"] if category != "Iterative Default" else ["Iterative Default"]

        web_app.include_router(router, tags=tag)


def add_routers_to_web_app(web_app: FastAPI):
    """
    Adds routers to the web app.

    Args:
        web_app: The FastAPI application to which routers will be added.
    """
    routers = find_api_routers_in_parent_project()
    logger.info(f"Adding router to web app")
    for project_name, router_list in routers.items():
        for router_dict in router_list:
            router = router_dict["router"]
            # Set the tags parameter to a unique value for each router
            web_app.include_router(router, tags=[f"{project_name}"])