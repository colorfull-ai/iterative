import sys
import uuid
import json
from functools import wraps
import os
import importlib.util
from iterative.cli import find_iterative_root

import logging

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
            logger.info(json.dumps(log_entry, indent=2))
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
