from iterative.models.iterative import IterativeModel
from typing import Optional

class IterativeAppConfig(IterativeModel):
    actions_search_path: Optional[str] = "actions"
    model_generation_path: Optional[str] = "models"
    tests_path: Optional[str] = "tests"
    utis_path: Optional[str] = "utils"
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