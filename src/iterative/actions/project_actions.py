import json
import os
import shutil
from iterative import get_config as _get_config
from iterative.api_processing import get_api_routers as _get_api_routers
from iterative.models.config import IterativeAppConfig
from iterative.utils import create_project_path as _create_project_path
import typer
from typing import Optional
from omegaconf import OmegaConf
from logging import getLogger as _get_logger

logger = _get_logger(__name__)

def create_folders(path: str):
    """
    Creates all folders needed for a given path if they don't exist.

    Args:
        path (str): The path of the directory to be created. This can be an absolute or relative path.

    Returns:
        None
    """
    if not os.path.exists(path):
        os.makedirs(path)

def create_actions_directory():
    """
    Creates a directory for actions if it doesn't exist.
    """
    actions_directory = os.path.join(_get_config().get("actions_search_path"))
    create_folders(actions_directory)

def create_services_directory():
    """
    Creates a directory for services if it doesn't exist.
    """
    services_directory = os.path.join(_get_config().get("services_generation_path"))
    create_folders(services_directory)

def create_data_directory():
    """
    Creates a directory for data if it doesn't exist.
    """
    data_directory = os.path.join(_get_config().get("data_path"))
    create_folders(data_directory)

def create_logs_directory():
    """
    Creates a directory for logs if it doesn't exist.
    """
    logs_directory = os.path.join(_get_config().get("logs_path"))
    create_folders(logs_directory)

def create_tests_directory():
    """
    Creates a directory for tests if it doesn't exist.
    """
    tests_directory = os.path.join(_get_config().get("tests_path"))
    create_folders(tests_directory)

def get_project_config():
    """
    Returns the project configuration.
    """

    return _get_config()

def get_config_schema():
    """
    Returns the schema for the project configuration.
    """

    print(IterativeAppConfig.schema())
    return IterativeAppConfig.schema()

def set_config_value(key: str, value: str):
    f"""
    Sets a configuration value.

    Schema:
    {json.dumps(get_config_schema(), indent=2)}
    """

    _get_config()[key] = value


def init(template_name: str = "starter"):
    """
    Initialize a new iterative app by copying the contents of a specific template directory to the current working directory.

    Args:
        template_name (str): The name of the template to be initialized.
    """
    template_name = "starter"

    # Define the paths
    package_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(package_dir)
    template_dir = os.path.join(parent_dir, 'templates', "init", template_name)
    target_dir = os.getcwd()

    # Check if the template directory exists
    if not os.path.exists(template_dir):
        typer.echo(f"Template '{template_name}' not found at {template_dir}")
        raise typer.Exit(code=1)

    try:
        # Copy each item from the template directory to the target directory
        for item in os.listdir(template_dir):
            source_item = os.path.join(template_dir, item)
            target_item = os.path.join(target_dir, item)

            # If it's a directory, use shutil.copytree, else use shutil.copy
            if os.path.isdir(source_item):
                shutil.copytree(source_item, target_item, dirs_exist_ok=True)
            else:
                shutil.copy(source_item, target_item)

        typer.echo(f"Initialized new iterative app with contents from template '{template_name}' in {target_dir}")
    except Exception as e:
        typer.echo(f"Error initializing app with template '{template_name}': {e}")
        raise typer.Exit(code=1)
    

def create_or_overwrite_script(script_name: str, script_content: str, actions_folder: str = 'actions'):
    """
    Creates or overwrites a Python script in the specified actions folder within the user's working directory.

    """
    # Ensure the script name ends with '.py'
    if not script_name.endswith('.py'):
        script_name += '.py'

    # Get the full path for the actions folder and ensure it exists
    # actions_path = os.path.join(os.getcwd(), actions_folder)
    actions_path = _create_project_path(actions_folder)
    os.makedirs(actions_path, exist_ok=True)

    # Full path for the script file
    script_file_path = os.path.join(actions_path, script_name)

    # Write the content to the script file, overwriting any existing content
    with open(script_file_path, 'w') as file:
        file.write(script_content)

    print(f"Script '{script_name}' has been created/overwritten at '{script_file_path}'")


def read_script_content(script_name: str, folder_to_read_from: str = 'service') -> str:
    """
    Reads the content of a specified script file from the actions folder.

    Returns:
        str: The content of the script file as a string.
    """
    # Construct the full file path
    script_file_path = os.path.join(os.getcwd(), folder_to_read_from, script_name)


    # Check if the file exists
    if not os.path.exists(script_file_path):
        return f"Script file '{script_file_path}' does not exist."

    # Read and return the file content
    try:
        with open(script_file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading script file: {e}"


def move_folder_within_app(source: str, destination: str) -> Optional[str]:
    """
    Moves a folder within the current Iterative app.

    Args:
        source (str): The path of the folder to move. This must be a path within the current Iterative app.
        destination (str): The path to move the folder to. This must be a path within the current Iterative app.

    Returns:
        Optional[str]: An error message if the move operation failed, or None if it succeeded.
    """
    # Check if source and destination are within an Iterative app
    if not (os.path.exists(os.path.join(source, '.iterative')) and os.path.exists(os.path.join(destination, '.iterative'))):
        return "Source or destination is not within an Iterative app."

    # Try to move the folder
    try:
        shutil.move(source, destination)
    except Exception as e:
        return f"Error moving folder: {e}"

    return None


def get_project_config():
    try:
        config = _get_config()
        # Convert the configuration to a dictionary or another suitable format for display or use
        config_dict = OmegaConf.to_object(config.config, resolve=True)
        return config_dict
    except Exception as e:
        logger.error(f"Error getting project configuration: {e}")
        return None


def initialize_project(project_name):
    project_dir = os.path.join(os.getcwd(), project_name)
    iterative_dir = os.path.join(project_dir, '.iterative')
    os.makedirs(iterative_dir, exist_ok=True)


def update_project_config(key, value):
    try:
        config = _get_config()
        # Assuming the configuration is a nested dictionary, update the relevant key
        OmegaConf.update(config.config, key, value, merge=True)
        # Save the updated configuration back to the file
        with open(config.find_iterative_config(), 'w') as f:
            OmegaConf.save(config=config.config, f=f)
        return True
    except Exception as e:
        logger.error(f"Error updating project configuration: {e}")
        return False
    
def update_project_config_value(key: str, value):
    config = _get_config()
    OmegaConf.update(config.config, key, value, merge=True)
    save_config(config)
    return f"Updated {key} to {value}"

def save_config():
    config_path = os.getcwd() + "/.iterative/config.yaml"
    if config_path:
        with open(config_path, 'w') as f:
            OmegaConf.save(config=_get_config().config, f=f)
        logger.info(f"Configuration saved to {config_path}")
    else:
        raise FileNotFoundError("Configuration file not found.")

def find_routers():
    
    return _get_api_routers()