import os
import shutil
from iterative.service.utils.project_utils import resolve_project_folder_path as _resolve_project_folder_path
import typer
from logging import getLogger as _get_logger

logger = _get_logger(__name__)

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
    actions_path = _resolve_project_folder_path(actions_folder)
    os.makedirs(actions_path, exist_ok=True)

    # Full path for the script file
    script_file_path = os.path.join(actions_path, script_name)

    # Write the content to the script file, overwriting any existing content
    with open(script_file_path, 'w') as file:
        file.write(script_content)

    logger.info(f"Script '{script_name}' has been created/overwritten at '{script_file_path}'")


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
