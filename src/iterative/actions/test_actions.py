import os
from typing import  Optional
from logging import getLogger as _getLogger
from iterative.service.project_management.service.project_utils import get_project_root as _get_project_root
import pytest

logger = _getLogger(__name__)


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
    project_root = _get_project_root(os.getcwd())
    # Define the path to the tests directory
    tests_dir = os.path.join(project_root, 'tests')

    # Check if the tests directory exists
    if not os.path.exists(tests_dir):
        logger.error("Tests directory does not exist in the current working directory.")
        return

    # Prepare the pytest command
    if test_name:
        # Run a specific test file
        test_file = os.path.join(tests_dir, test_name + '.py')
        if not os.path.exists(test_file):
            logger.error(f"Test file '{test_name}.py' does not exist in the tests directory.")
            return
        pytest.main([test_file])
    else:
        # Run all tests
        pytest.main([tests_dir])