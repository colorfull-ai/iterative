import json
import os
from iterative.service.service_management.service.json_encoder import CustomEncoder
from pydantic import BaseModel
import importlib.util
import sys

import logging


logger = logging.getLogger(__name__)

def load_model_schema(model_path: str, model_name: str) -> str:
    """
    Load the Pydantic model schema from the given model path and name.

    Args:
        model_path (str): The path to the Python module containing the Pydantic model.
        model_name (str): The name of the Pydantic model class.

    Returns:
        str: The JSON schema representation of the Pydantic model.

    Raises:
        ValueError: If the Pydantic model cannot be found or is not a valid BaseModel.
    """
    module_name, class_name = model_name.rsplit('.', 1)  # split the module name and the class name
    spec = importlib.util.spec_from_file_location(module_name, model_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    model_class = getattr(module, class_name, None)
    if model_class:
        if issubclass(model_class, BaseModel):
            return json.dumps(model_class.schema(), indent=4, cls=CustomEncoder)
        else:
            logger.debug(f"{model_class} is not a subclass of BaseModel")
    else:
        logger.warning(f"Class {class_name} not found in {model_path}.")
    return "{}"
