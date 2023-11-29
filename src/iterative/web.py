# util_server.py in admin_code subdirectory
import os
from fastapi import  FastAPI
from fastapi.responses import RedirectResponse
from iterative.config import get_config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from iterative.util_server import discover_actions
from iterative.user_cli import cli_app

web_app = FastAPI()

@web_app.on_event("startup")
def startup_event():
    discover_actions(cli_app, web_app)

@web_app.get("/")
def root():
    # redirect to docs
    return RedirectResponse(url='/docs')

def custom_openapi():
    if web_app.openapi_schema:
        return web_app.openapi_schema
    
    app_name = get_config().config.get("app_name", "Iterative App")
    version = get_config().config.get("version", "v0.1.0")
    description = get_config().config.get("description", "Initial Iterative APP Backend.")

    openapi_schema = get_openapi(
        title=app_name,
        version=version,
        description=description,
        routes=web_app.routes,
    )
    
    openapi_schema["servers"] = [
        {
            "url": os.getenv('HOST'),
        }
    ]

    web_app.openapi_schema = openapi_schema
    return web_app.openapi_schema

web_app.openapi = custom_openapi

# Add CORS middleware
origins = [
    "*"
    # Add any other origins you want to whitelist here
]


web_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)