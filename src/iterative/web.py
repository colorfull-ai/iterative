# util_server.py in admin_code subdirectory
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from iterative import get_project_root
from iterative.config import get_config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from logging import getLogger
from fastapi.staticfiles import StaticFiles

logger = getLogger(__name__)

iterative_user_web_app = FastAPI()


def get_swagger_ui_path():
    """
    Returns the path to the custom Swagger UI, if it exists.

    Returns:
        str: The path to the custom Swagger UI, or None if the default UI should be used.
    """
    project_root = get_project_root()
    extra_ui_path = get_config().get("swagger_ui_nested_path")
    if extra_ui_path:
        return os.path.join(project_root, "service", "swagger_ui", "service", extra_ui_path)
    else:
        return os.path.join(project_root, "service", "swagger_ui", "service")

@iterative_user_web_app.on_event("startup")
def startup_event():
    """
    This function is called when the server starts.
    It checks if a custom Swagger UI exists, and mounts it at /custom-docs if it does.
    """
    custom_swagger_ui_path = get_swagger_ui_path()

    # Check if the custom Swagger UI exists
    if os.path.exists(custom_swagger_ui_path):
        # If it exists, mount it at "/custom-docs"
        iterative_user_web_app.mount("/custom-docs", StaticFiles(directory=custom_swagger_ui_path, html=True), name="custom_swagger_ui")

@iterative_user_web_app.get("/")
def root():
    """
    Returns the root endpoint of the API.

    If a custom Swagger UI is available, this endpoint will redirect to it.
    Otherwise, it will redirect to the default Swagger UI.

    Returns:
        RedirectResponse: A redirect response to the appropriate Swagger UI.
    """
    custom_swagger_ui_path = get_swagger_ui_path()

    # Check if the custom Swagger UI exists
    if os.path.exists(custom_swagger_ui_path):
        # If it exists, redirect to the custom Swagger UI
        return RedirectResponse(url="/custom-docs")
    else:
        # If it doesn't exist, let FastAPI serve the default Swagger UI
        return RedirectResponse(url="/docs")


def custom_openapi():
    """
    This function creates a custom OpenAPI schema for the FastAPI application.
    It uses the get_openapi function from fastapi.openapi.utils to generate the schema,
    and adds the HOST environment variable as a server URL.
    """
    if iterative_user_web_app.openapi_schema:
        return iterative_user_web_app.openapi_schema

    app_name = get_config().config.get("app_name", "Iterative App")
    version = get_config().config.get("version", "v0.1.0")
    description = get_config().config.get(
        "description", "Initial Iterative APP Backend."
    )

    openapi_schema = get_openapi(
        title=app_name,
        version=version,
        description=description,
        routes=iterative_user_web_app.routes,
    )

    openapi_schema["servers"] = [
        {
            "url": os.getenv("HOST"),
        },
        {
            "url": f"http://{get_config().get('fastapi_host')}:{get_config().get('fastapi_port')}",
        }
    ]

    iterative_user_web_app.openapi_schema = openapi_schema
    return iterative_user_web_app.openapi_schema


iterative_user_web_app.openapi = custom_openapi

# Add CORS middleware
origins = [
    "*"
    # Add any other origins you want to whitelist here
]


iterative_user_web_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
