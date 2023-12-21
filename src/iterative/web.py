# util_server.py in admin_code subdirectory
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from iterative.service.utils.action_utils import get_all_actions
from iterative.config import get_config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
# from iterative.web_app_integration import integrate_actions_into_web_app
from logging import getLogger

logger = getLogger(__name__)

iterative_user_web_app = FastAPI()


@iterative_user_web_app.on_event("startup")
def startup_event():
    from iterative import prep_app
    prep_app()


@iterative_user_web_app.get("/")
def root():
    # redirect to docs
    return RedirectResponse(url="/docs")


def custom_openapi():
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
