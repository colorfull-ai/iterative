import json
import os
import shutil
from iterative import get_config as _get_config
from iterative.models.config import IterativeAppConfig
import typer

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