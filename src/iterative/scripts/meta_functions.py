# main module (where you start the server)

import os
from typing import Dict
import requests
from iterative.config import get_config
from fastapi.responses import JSONResponse

def get_openapi_schema() -> Dict:
    """
    Fetch the OpenAPI schema from the FastAPI application.

    Returns:
    dict: The OpenAPI schema as a dictionary.
    """
    from iterative.web import web_app
    return JSONResponse(web_app.openapi_schema)