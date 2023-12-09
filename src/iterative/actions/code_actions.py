import os
import subprocess
from typing import List, Optional
from logging import getLogger as _getLogger

logger = _getLogger(__name__)

def get_latest_updated_files(dir_path: str, num_files: int = 5) -> List[str]:
    """
    Get the latest updated files in a directory.

    Args:
        dir_path (str): The directory path.
        num_files (int, optional): The number of files to return. Defaults to 5.

    Returns:
        List[str]: The paths of the latest updated files.
    """
    files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[:num_files]

def read_files(files: List[str]) -> str:
    """
    Read the contents of multiple files and concatenate them into a single string.

    Args:
        files (List[str]): The file paths.

    Returns:
        str: The concatenated file contents.
    """
    contents = ""
    for file in files:
        with open(file, 'r') as f:
            contents += f.read()
    return contents

def get_code_dir_context_similarity(dir_path: str) -> str:
    """
    Given a dir path, reads the latest updated files and a few medium sized files as a big concatenated string of code
    and context about the code.

    Args:
        dir_path (str): The directory path.

    Returns:
        str: The concatenated file contents.
    """
    latest_files = get_latest_updated_files(dir_path)
    contents = read_files(latest_files)
    return contents

def run_tests(test_name: Optional[str] = None):
    """
    Run pytest in the tests directory of the current working directory.
    If a test name is provided, runs that specific test file; otherwise, runs all tests.

    Args:
        test_name (Optional[str]): The name of the test file (without .py extension), or None to run all tests.

    Returns:
        None: Prints the output of the pytest command.
    """
    logger.info("SETTING TEST_MODE ENVIRONMENT VARIABLE TO TRUE")
    os.environ["TEST_MODE"] = "True"
    # Define the path to the tests directory
    tests_dir = os.path.join(os.getcwd(), 'tests')

    # Check if the tests directory exists
    if not os.path.exists(tests_dir):
        print("Tests directory does not exist in the current working directory.")
        return

    # Prepare the pytest command
    if test_name:
        # Run a specific test file
        test_file = os.path.join(tests_dir, test_name + '.py')
        if not os.path.exists(test_file):
            print(f"Test file '{test_name}.py' does not exist in the tests directory.")
            return
        pytest_command = ["pytest", test_file]
    else:
        # Run all tests
        pytest_command = ["pytest", tests_dir]

    # Run pytest
    try:
        result = subprocess.run(pytest_command, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error while running pytest:")
        print(e.output)


