import shutil
import os
from iterative.service.project_management.service.project_utils import get_project_root, get_parent_project_root
from iterative.service.service_management.service.service_utils import get_service_name
import yaml
from logging import getLogger

logger = getLogger(__name__)


def copy_template_to_target(template_dir: str, target_dir: str):
    """
    Copy each item from the template directory to the target directory.

    Args:
        template_dir (str): The directory of the template to be copied.
        target_dir (str): The directory where the template should be copied to.
    """
    try:
        for item in os.listdir(template_dir):
            source_item = os.path.join(template_dir, item)
            target_item = os.path.join(target_dir, item)

            if os.path.isdir(source_item):
                shutil.copytree(source_item, target_item, dirs_exist_ok=True)
            else:
                shutil.copy(source_item, target_item)
    except Exception as e:
        logger.error(f"Error copying template to target: {e}")
        raise

def get_template_dir(template_name: str):
    """
    Get the directory of the specified template.

    Args:
        template_name (str): The name of the template.

    Returns:
        str: The directory of the template.
    """
    parent_dir = get_project_root(__file__)
    template_dir = os.path.join(parent_dir, 'templates', 'init', template_name)
    return template_dir

def validate_template_exists(template_dir: str, template_name: str):
    """
    Validate that the specified template directory exists.

    Args:
        template_dir (str): The directory of the template.
        template_name (str): The name of the template.

    Raises:
        FileNotFoundError: If the template directory does not exist.
    """
    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"Template '{template_name}' not found at {template_dir}")

def init_project(template_name: str = "starter"):
    """
    Initialize a new iterative app by copying the contents of a specific template directory to the current working directory.

    Args:
        template_name (str): The name of the template to be initialized.
    """
    template_dir = get_template_dir(template_name)
    validate_template_exists(template_dir, template_name)

    try:
        copy_template_to_target(template_dir, get_project_root())
        logger.info(f"Successfully initialized app with template '{template_name}'")
    except Exception as e:
        logger.error(f"Error initializing app with template '{template_name}': {e}")