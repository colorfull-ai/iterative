# util_server.py in admin_code subdirectory
import subprocess
import time
import os
import importlib.util
import inspect
from fastapi import APIRouter, HTTPException
from .config import get_config
from typing import Callable, get_type_hints
import uuid
import json
from functools import wraps
from .logger import get_logger


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

def load_routers_from_directory(directory, web_app):
    # Skip if the directory doesn't exist
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    # Search for Python scripts in the provided directory and load routers
    for file in os.listdir(directory):
        if file.endswith(".py") and not file.startswith("_"):
            full_path = os.path.join(directory, file)
            module_name = os.path.splitext(file)[0]
            module = load_module_from_path(full_path)

            # Assuming each script has a router named 'router'
            if hasattr(module, "router"):
                web_app.include_router(module.router)

def discover_actions(cli_app, web_app):
    # Get the global configuration
    config = get_config()
    if not config.get("discover_actions"):
        return
    
    user_scripts_path = config.get("scripts_search_path")

    # Directory containing the default scripts
    default_scripts_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
    # Process default scripts
    process_scripts_directory(default_scripts_directory, cli_app, web_app, script_source="Iterative Default")
    endpoints_directory = os.path.join(os.getcwd(), "endpoints")
    load_routers_from_directory(endpoints_directory, web_app)

    # Process user scripts
    if user_scripts_path:
        if user_scripts_path == ".":
            iterative_app_scripts_directory = os.path.join(os.getcwd(), "scripts")
            process_scripts_directory(iterative_app_scripts_directory, cli_app, web_app, script_source="User Script")

def process_scripts_directory(directory, cli_app, web_app, script_source):
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

                    # Set tags based on the script source
                    tag = None
                    if script_source == "Iterative Default":
                        tag = ["Iterative Default"]
                    else:
                        # Here, you can also prepend the script file name or any other identifier
                        tag = [f"{script_source}: {file.replace('.py', '')}"]

                    web_app.include_router(router, tags=tag)
                    logged_func = log_function_call(func)  # Apply decorator
                    cli_app.command(name=snake_name)(logged_func)


def run_ngrok_setup_script(script_path):
    try:
        subprocess.run(["bash", script_path], check=True)

        # Wait for ngrok to set up completely (30 seconds)
        print("Waiting for ngrok to set up...")
        time.sleep(8)

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


import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_any_event(self, event):
        self.callback()

def start_uvicorn(host, port, app_module):
    subprocess.run(["pkill", "-f", f"uvicorn.*{port}"])
    time.sleep(1)  # Allow time for the port to become free
    return subprocess.Popen(["uvicorn", app_module, "--host", host, "--port", str(port)])

def run_ngrok_subprocess():
    # Set up ngrok (assuming you have this function implemented)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    bash_script_path = os.path.join(script_directory, "run_ngrok.sh")
    run_ngrok_setup_script(bash_script_path)

def run_web_server(port: int):
    host = "0.0.0.0"
    app_module = "iterative.web:web_app"

    # Set up ngrok (assuming you have this function implemented)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    bash_script_path = os.path.join(script_directory, "run_ngrok.sh")
    run_ngrok_setup_script(bash_script_path)

    uvicorn_process = start_uvicorn(host, port, app_module)

    def restart_uvicorn():
        nonlocal uvicorn_process
        print("Restarting Detected Changes restarting server... ")
        uvicorn_process.kill()
        uvicorn_process.wait()
        uvicorn_process = start_uvicorn(host, port, app_module)

    # Watchdog configuration
    reload_dirs = get_config().get('reload_dirs', [])
    # Add the parent directory of this file (iterative package root)
    iterative_package_root = os.path.dirname(script_directory)
    reload_dirs.append(iterative_package_root)

    event_handler = ChangeHandler(restart_uvicorn)
    observer = Observer()

    for directory in reload_dirs:
        observer.schedule(event_handler, directory, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        uvicorn_process.kill()

    observer.join()