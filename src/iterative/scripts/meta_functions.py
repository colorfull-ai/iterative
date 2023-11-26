# main module (where you start the server)

import os
import requests
from iterative.config import get_config


def get_openapi_schema() -> dict:
    """
    Fetch the OpenAPI schema from the FastAPI application.

    Returns:
    dict: The OpenAPI schema as a dictionary.
    """
    from iterative.web import web_app
    return web_app.openapi_schema