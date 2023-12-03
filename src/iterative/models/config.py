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
    persist_cache_as_db: Optional[bool]
    default_ai_model: Optional[str]
    fastapi_port: Optional[int]
    fastapi_host: Optional[str]
    do_not_discover: Optional[bool]
    assistant_id: Optional[str]
    assistant_conversation_thread_id: Optional[str]
    discover_actions: Optional[bool]
    verbose: Optional[bool] = True
    logging_level: Optional[LoggingLevel] = LoggingLevel.INFO