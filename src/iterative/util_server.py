# util_server.py in admin_code subdirectory
import subprocess
import time
import typer
import os
import importlib.util
import inspect
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from .config import get_config
from typing import Callable, get_type_hints
import uuid
import json
from functools import wraps
from fastapi.openapi.utils import get_openapi

import uvicorn
from .logger import get_logger

cli_app = typer.Typer()
web_app = FastAPI()

@web_app.get("/")
def root():
    # redirect to docs
    return RedirectResponse(url='/docs')

def custom_openapi():
    if web_app.openapi_schema:
        return web_app.openapi_schema
    
    app_name = get_config().config.get("app_name", "Iterative App")
    version = get_config().config.get("version", "v0.1.0")
    description = get_config().config.get("description", "Initial Iterative APP Backend.")

    openapi_schema = get_openapi(
        title=app_name,
        version=version,
        description=description,
        routes=web_app.routes,
    )
    
    openapi_schema["servers"] = [
        {
            "url": os.getenv('HOST'),
        }
    ]

    web_app.openapi_schema = openapi_schema
    return web_app.openapi_schema

web_app.openapi = custom_openapi

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
    config = get_config()
    user_scripts_path = config.get("scripts_search_path")

    # Directory containing the default scripts
    default_scripts_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

    # Process default scripts
    process_scripts_directory(default_scripts_directory, cli_app, web_app)

    # If user provided a scripts path, process those scripts as well
    if user_scripts_path:
        if user_scripts_path == ".":
            iterative_app_scripts_directory = os.path.join(os.getcwd(), "scripts")
            process_scripts_directory(iterative_app_scripts_directory, cli_app, web_app)

def process_scripts_directory(directory, cli_app, web_app):
    # Skip if the directory doesn't exist
    if not os.path.exists(directory):
        print(f"'scripts' directory not found in {directory}")
        return

    # Search for Python scripts in the provided directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                module = load_module_from_path(full_path)
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    # Skip private functions
                    if name.startswith('_'):
                        continue
                    snake_name = snake_case(name)
                    router = create_endpoint(func, snake_name)
                    
                    web_app.include_router(router)
                    logged_func = log_function_call(func)  # Apply decorator
                    cli_app.command(name=snake_name)(logged_func)


def run_ngrok_setup_script(script_path):
    try:
        subprocess.run(["bash", script_path], check=True)

        # Wait for ngrok to set up completely (30 seconds)
        print("Waiting for ngrok to set up...")
        time.sleep(15)

        # Read environment variables from the temp file
        with open('/tmp/env_vars.txt', 'r') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

        print(f"HOST variable set to: {os.environ.get('HOST')}")
        print("ngrok and environment variables set up successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the ngrok setup script: {e}")
    except IOError as e:
        print(f"Error reading environment variables from temp file: {e}")


def run_web_server(port: int):
    # Construct the path to the Bash script dynamically
    script_directory = os.path.dirname(os.path.abspath(__file__))
    bash_script_path = os.path.join(script_directory, "run_ngrok.sh")

    # Run the Bash script to set up ngrok and environment variables
    run_ngrok_setup_script(bash_script_path)

    # Now, environment variables are set, and you can access them if needed
    # For example: os.environ.get('WEBHOOK_DEV_LINK')

    host = "0.0.0.0"
    os.environ['FASTAPI_HOST'] = host
    os.environ['FASTAPI_PORT'] = str(port)
    uvicorn.run(web_app, host=host, port=port)