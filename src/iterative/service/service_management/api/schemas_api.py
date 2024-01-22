import os
from fastapi import APIRouter
from typing import Dict
from iterative.service.project_management.service.project_utils import find_pydantic_models_in_models_folders, get_project_root
from iterative.service.service_management.service.utils import load_model_schema
import json


router = APIRouter()

import logging

logger = logging.getLogger(__name__)


@router.get("/model_schemas", response_model=Dict[str, Dict[str, Dict]])
def get_model_schemas():
    try:
        logger.info("Starting to get model schemas.")
        project_root = get_project_root()  # replace with your project root directory
        pydantic_models = find_pydantic_models_in_models_folders(project_root)

        model_schemas = {}
        for model_name, model_path in pydantic_models.items():
            model_schema_json = load_model_schema(model_path, model_name)
            model_schema = json.loads(model_schema_json)

            # Extract the service name from the model path
            path_parts = model_path.split(os.sep)
            if 'service' in path_parts:
                service_index = path_parts.index('service')
                if len(path_parts) > service_index + 1:
                    service_name = path_parts[service_index + 1]
                    if service_name not in model_schemas:
                        model_schemas[service_name] = {}
                    model_schemas[service_name][model_name] = model_schema

        logger.info("Successfully got model schemas.")
        return model_schemas
    except Exception as e:
        logger.error("Failed to get model schemas.", exc_info=True)
        raise