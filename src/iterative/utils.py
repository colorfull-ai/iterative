from datetime import date, timezone
import datetime
from enum import Enum
import sys
from typing import List
import uuid
import json
from functools import wraps
import os
import importlib.util
from fastapi import Response
from iterative.cli import find_iterative_root
from requests import Response as RequestsResponse

import logging

from iterative.models.action import Action
from pydantic import BaseModel

def log_function_call(func):
    logger = logging.getLogger(func.__name__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        event_id = str(uuid.uuid4())
        input_payload = {'args': args, 'kwargs': kwargs}

        try:
            result = func(*args, **kwargs)
            log_entry = {
                'event_id': event_id,
                'event': func.__name__,
                'input': input_payload,
                'output': result
            }
            logger.info(json.dumps(log_entry, indent=2, cls=CustomEncoder))
            return result
        except Exception as e:
            log_entry = {
                'event_id': event_id,
                'event': func.__name__,
                'input': input_payload,
                'error': str(e)
            }
            logger.error(json.dumps(log_entry, indent=2))
            raise e
    return wrapper


def snake_case(s: str) -> str:
    return s.replace("-", "_").replace(" ", "_")

def load_module_from_path(path: str):
    # Add the directory containing 'models' to sys.path
    root_directory = find_iterative_root(os.getcwd())
    if root_directory not in sys.path:
        sys.path.insert(0, root_directory)

    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_openai_functions(actions: List[Action]):
    # Get the path to the openai_functions.py file
    root_directory = find_iterative_root(os.getcwd())
    openai_functions_path = os.path.join(root_directory, 'openai_functions.py')

    # Load the module
    openai_functions = load_module_from_path(openai_functions_path)

    # Get the functions
    functions = []
    for name in dir(openai_functions):
        if name.startswith('_'):
            continue
        obj = getattr(openai_functions, name)
        if callable(obj):
            functions.append(obj)
    return functions


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, BaseModel):
            return obj.dict(by_alias=True, exclude_none=True)
        elif isinstance(obj, datetime.datetime):
            return (
                obj.replace(tzinfo=timezone.utc).isoformat()
                if obj.tzinfo is None
                else obj.isoformat()
            )
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Response):
            # Handle FastAPI Response objects
            return {
                "status_code": obj.status_code,
                "headers": dict(obj.headers),
                "body": str(obj.body) if obj.body else None,
            }
        elif isinstance(obj, RequestsResponse):
            # Handle Requests Response objects
            return {
                "status_code": obj.status_code,
                "headers": dict(obj.headers),
                "body": obj.text,
            }
        elif isinstance(obj, (list, set)):
            return [self.default(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.default(v) for k, v in obj.items()}
        else:
            return json.JSONEncoder.default(self, obj)