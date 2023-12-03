# main module (where you start the server)

import json
import os
from typing import Dict
from iterative.cache import cache
from logging import getLogger as _getLogger

logger = _getLogger(__name__)


def get_openapi_schema() -> Dict:
    """
    Fetch the OpenAPI schema from the FastAPI application.

    Returns:
    dict: The OpenAPI schema as a dictionary.
    """
    from iterative import web_app

    logger.debug(web_app.openapi())

    return web_app.openapi()

def generate_directory_tree(startpath: str = '.') -> str:
    """
    Generates a string representing the tree structure of the directory,
    ignoring __pycache__ directories.

    Args:
        startpath (str): The starting directory path. Defaults to the current directory.

    Returns:
        str: A string representation of the directory tree.
    """
    tree = []

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d != '__pycache__']  # Ignore __pycache__
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.endswith('.pyc'):  # Optionally ignore .pyc files
                tree.append(f"{subindent}{f}")

    tree_str = '\n'.join(tree)
    logger.debug(tree_str)

    return tree_str


def get_local_db_metrics() -> str:
    """
    Generates metrics about the cache in JSON format, including detailed statistics for each collection.

    Returns:
        str: A JSON string containing metrics about the cache.
    """
    metrics = {}
    collections = cache.collections

    # Total number of collections
    metrics['total_collections'] = len(collections)

    # Detailed metrics for each collection
    for collection_name, documents in collections.items():
        total_documents = len(documents)
        metrics[collection_name] = {
            'total_documents': total_documents
        }

        # Calculate additional metrics per collection
        if total_documents > 0:
            total_fields = sum(len(doc.keys()) for doc in documents.values())
            max_fields = max(len(doc.keys()) for doc in documents.values())
            min_fields = min(len(doc.keys()) for doc in documents.values())
            avg_fields = total_fields / total_documents

            metrics[collection_name].update({
                'average_fields_per_document': avg_fields,
                'max_fields_in_document': max_fields,
                'min_fields_in_document': min_fields
            })
    metrics = json.dumps(metrics, indent=4)

    logger.debug(metrics)

    # Convert the metrics dictionary to a JSON string
    return metrics

