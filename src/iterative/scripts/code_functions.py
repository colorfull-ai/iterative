import os

def create_or_overwrite_script(script_name: str, script_content: str, scripts_folder: str = 'scripts'):
    """
    Creates or overwrites a Python script in the specified scripts folder within the user's working directory.

    """
    # Ensure the script name ends with '.py'
    if not script_name.endswith('.py'):
        script_name += '.py'

    # Get the full path for the scripts folder and ensure it exists
    scripts_path = os.path.join(os.getcwd(), scripts_folder)
    os.makedirs(scripts_path, exist_ok=True)

    # Full path for the script file
    script_file_path = os.path.join(scripts_path, script_name)

    # Write the content to the script file, overwriting any existing content
    with open(script_file_path, 'w') as file:
        file.write(script_content)

    print(f"Script '{script_name}' has been created/overwritten at '{script_file_path}'")


def read_script_content(script_name: str, scripts_folder: str = 'scripts') -> str:
    """
    Reads the content of a specified script file from the scripts folder.

    Returns:
        str: The content of the script file as a string.
    """
    # Construct the full file path
    script_file_path = os.path.join(os.getcwd(), scripts_folder, script_name)

    # Check if the file exists
    if not os.path.exists(script_file_path):
        return f"Script file '{script_file_path}' does not exist."

    # Read and return the file content
    try:
        with open(script_file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading script file: {e}"

