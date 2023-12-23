import os
from textwrap import dedent as _dedent
from typing import  Optional
import humps
from iterative.config import get_config as _get_config
from iterative.service.utils.project_utils import resolve_project_folder_path as _resolve_project_folder_path
from logging import getLogger as _getLogger

logger = _getLogger(__name__)

def generate_model(entity_name: str, model_generation_path: Optional[str] = None):
    """
    Create a basic nosql_yorm model file with the given entity name in a 'models' directory.
    Also updates __init__.py to import the new model and add it to the __all__ list.
    """
    # Fetch the model generation path from the global configuration if not provided
    if not model_generation_path:
        model_generation_path = _get_config().get('model_generation_path')

    # Append 'models' to the model generation path to ensure the directory structure
    model_folder = _resolve_project_folder_path(model_generation_path)

    # Create the models directory if it doesn't exist
    try:
        os.makedirs(model_folder, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating directory {model_folder}: {e}")
        return

    # Generate file name in snake case and class name in pascal case
    file_name = humps.decamelize(entity_name) + ".py"
    class_name = humps.pascalize(entity_name)

    file_path = os.path.join(model_folder, file_name)
    model_content = _dedent(f"""\
    from iterative import IterativeModel
    from typing import *
    from iterative.models import * 
                            

    class {class_name}(IterativeModel):
        _collection_name = "{class_name}"
        # TODO: Add fields here
    """)

    # Write the model class to the file
    with open(file_path, 'w') as file:
        file.write(model_content)

    logger.info(f"Model {class_name} created at {file_path}")
    return model_content