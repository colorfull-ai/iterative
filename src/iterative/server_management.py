# util_server.py in admin_code subdirectory
import subprocess
import time
import os
import subprocess
import os
from logging import getLogger

logger = getLogger(__name__)


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

    prep_app()

    # Set up ngrok (assuming you have this function implemented)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    bash_script_path = os.path.join(script_directory, "run_ngrok.sh")
    run_ngrok_setup_script(bash_script_path)



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
