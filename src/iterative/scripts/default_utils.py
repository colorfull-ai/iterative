# main module (where you start the server)

import os
import requests
from iterative.config import _shared_config


def get_openapi_schema() -> dict:
    """
    Fetch the OpenAPI schema from the FastAPI application.

    Returns:
    dict: The OpenAPI schema as a dictionary.
    """
    config = _shared_config
    host_const = "FASTAPI_HOST"
    port_const = "FASTAPI_PORT"
    host = os.environ.get(host_const)
    port = os.environ.get(port_const)
    
    # Fetch host and port from environment variables
    host = host or config.get(host_const, "0.0.0.")
    port = port or config.get(port_const, "5279")

    openapi_url = f"http://{host}:{port}/openapi.json"
    response = requests.get(openapi_url)
    return response.json()