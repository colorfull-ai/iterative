# util_server.py in admin_code subdirectory
import subprocess
import time
import os
from iterative.config import get_config
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logging import getLogger

logger = getLogger(__name__)


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

def run_web_server():
    """
    Run the fastapi web server over uvicorn.  Settings are taken from .iterative/config.yaml
    """
    from iterative import prep_app

    host = get_config().get("fastapi_host", "0.0.0.0")
    port = get_config().get("fastapi_port", 5279)
    app_module = "iterative.web:iterative_user_web_app"

    prep_app()

    # Set up ngrok (assuming you have this function implemented)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    bash_script_path = os.path.join(script_directory, "run_ngrok.sh")
    run_ngrok_setup_script(bash_script_path)

    uvicorn_process = start_uvicorn(host, port, app_module)

    def restart_uvicorn():

        nonlocal uvicorn_process
        logger.info("Restarting Detected Changes restarting server... ")
        uvicorn_process.kill()
        uvicorn_process.wait()

        prep_app()
        uvicorn_process = start_uvicorn(host, port, app_module)

    # Watchdog configuration
    reload_dirs = get_config().get('reload_dirs', [])
    logger.info(f"Watching directories for changes: {reload_dirs}")
    # Add the parent directory of this file (iterative package root)

    event_handler = ChangeHandler(restart_uvicorn)
    observer = Observer()

    if get_config().get("reload", False):
        logger.info("Reload enabled.  Watching directories for changes...")
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


def run_ngrok_setup_script(script_path):
    try:
        subprocess.run(["bash", script_path], check=True)

        # Wait for ngrok to set up completely (30 seconds)
        logger.info("Waiting for ngrok to set up...")
        time.sleep(8)

        # Read environment variables from the temp file
        with open('/tmp/env_vars.txt', 'r') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

        logger.info(f"HOST variable set to: {os.environ.get('HOST')}")
        logger.info("ngrok and environment variables set up successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while running the ngrok setup script: {e}")
    except IOError as e:
        logger.error(f"Error reading environment variables from temp file: {e}")
