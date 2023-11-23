# util_server.py in admin_code subdirectory
import typer
import os
import importlib.util
import inspect
from fastapi import APIRouter, FastAPI, HTTPException
from .config import _get_global_config
from typing import Callable, get_type_hints
import uuid
import json
from functools import wraps

import uvicorn
from .logger import get_logger

cli_app = typer.Typer()
web_app = FastAPI()



def log_function_call(func):
    logger = get_logger(func.__name__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        event_id = str(uuid.uuid4())
        input_payload = {'args': args, 'kwargs': kwargs}

        try:
            result = func(*args, **kwargs)
            log_entry = {
                'event_id': event_id,
                'event': func.__name__,
                'input': input_payload,
                'output': result
            }
            logger.info(json.dumps(log_entry, indent=2))
            return result
        except Exception as e:
            log_entry = {
                'event_id': event_id,
                'event': func.__name__,
                'input': input_payload,
                'error': str(e)
            }
            logger.error(json.dumps(log_entry, indent=2))
            raise e
    return wrapper


def snake_case(s: str) -> str:
    return s.replace("-", "_").replace(" ", "_")

def load_module_from_path(path: str):
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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

def discover_scripts(cli_app, web_app):
    # Get the global configuration
    config = _get_global_config()

    # Directory of the script containing this function
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Path to the 'scripts' directory within the same directory as this script
    scripts_search_path = os.path.join(script_directory, 'scripts')

    # Check if the 'scripts' directory exists
    if not os.path.exists(scripts_search_path):
        print(f"'scripts' directory not found in {script_directory}")
        return

    # Search for Python scripts in the 'scripts' directory
    for root, dirs, files in os.walk(scripts_search_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                module = load_module_from_path(full_path)
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    # Skip private functions (those starting with an underscore)
                    if name.startswith('_'):
                        continue
                    snake_name = snake_case(name)
                    router = create_endpoint(func, snake_name)
                    
                    web_app.include_router(router)
                    logged_func = log_function_call(func)  # Apply decorator
                    cli_app.command(name=snake_name)(logged_func)

                        


def run_web_server(port: int):
    host = "0.0.0.0"
    os.environ['FASTAPI_HOST'] = host
    os.environ['FASTAPI_PORT'] = str(port)
    uvicorn.run(web_app, host=host, port=port)
