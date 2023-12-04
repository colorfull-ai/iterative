from enum import Enum
from iterative.models.iterative import IterativeModel
from typing import Optional
import logging

# logging level enum
class LoggingLevel(str, Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class IterativeAppConfig(IterativeModel):
    actions_search_path: Optional[str] = "actions"
    model_generation_path: Optional[str] = "models"
    services_generation_path: Optional[str] = "services"
    api_generation_path: Optional[str] = "api"
    data_path: Optional[str] = "data"
    logs_path: Optional[str] = "logs"
    tests_path: Optional[str] = "tests"
    reload_dirs: Optional[list[str]] = ["."]
    reload: Optional[bool] = True
    persist_cache_as_db: Optional[bool] = False
    default_ai_model: Optional[str] = "gpt-3.5-turbo"
    fastapi_port: Optional[int] = "8000"
    fastapi_host: Optional[str] = "0.0.0.0"
    assistant_id: Optional[str] = ""
    assistant_conversation_thread_id: Optional[str] = " "
    logging_level: Optional[str] = LoggingLevel.INFO.value
    run_ngrok: Optional[bool] = False