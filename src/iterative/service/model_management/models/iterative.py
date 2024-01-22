from nosql_yorm.models import BaseFirebaseModel
from enum import Enum
from typing import Optional
import logging


class IterativeModel(BaseFirebaseModel):
    ...


# logging level enum
class LoggingLevel(str, Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class IterativeAppConfig(IterativeModel):
    """
    If you want the new config variable to be available in the config object, you need to add it here.
    """

    actions_search_path: Optional[str] = "actions"
    model_generation_path: Optional[str] = "models"
    service_generation_path: Optional[str] = "service"
    api_generation_path: Optional[str] = "api"
    apps_path: Optional[str] = "apps"
    data_path: Optional[str] = "data"
    logs_path: Optional[str] = "logs"
    tests_path: Optional[str] = "tests"
    docs_path: Optional[str] = "docs"
    ui_path: Optional[str] = "ui"
    ui_clients_path: Optional[str] = "clients"
    ui_models_path: Optional[str] = "models"
    reload_dirs: Optional[list[str]] = ["."]  # Specify directories to be reloaded
    reload: Optional[bool] = True
    persist_cache_as_db: Optional[bool] = False
    read_write_to_cache: Optional[bool] = False
    default_ai_model: Optional[str] = "gpt-3.5-turbo"
    fastapi_port: Optional[int] = "8000"
    fastapi_host: Optional[str] = "0.0.0.0"
    assistant_id: Optional[str] = ""
    assistant_conversation_thread_id: Optional[str] = " "
    logging_level: Optional[str] = LoggingLevel.INFO.value
    run_ngrok: Optional[bool] = False
    expose_project_actions: Optional[bool] = True
    expose_package_default_actions: Optional[bool] = True
    expose_default_actions_to_ai: Optional[bool] = True
    expose_project_actions_to_ai: Optional[bool] = True
    expose_api_actions_to_ai: Optional[bool] = True
    expose_default_actions_to_cli: Optional[bool] = True
    expose_project_actions_to_cli: Optional[bool] = True
    actions_cap: Optional[int] = 128
    metadata: Optional[dict] = {}
