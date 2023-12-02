from functools import wraps
import os
from fastapi import APIRouter, HTTPException
from typing import Callable, get_type_hints
import inspect

from iterative.utils import load_module_from_path, snake_case

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
        print(f"Directory not found: {directory}")
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

def integrate_actions_into_web_app(actions, web_app):
    for action in actions:
        snake_name = snake_case(action['name'])
        router = create_endpoint(action['function'], snake_name)

        # Determine tags based on script source
        tag = [f"{action['script_source']}: {action['file'].replace('.py', '')}"] if action['script_source'] != "Iterative Default" else ["Iterative Default"]

        web_app.include_router(router, tags=tag)