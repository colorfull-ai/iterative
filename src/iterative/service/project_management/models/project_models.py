from typing import Optional
from pydantic import Field
from iterative.service.model_management.models.iterative import IterativeModel, IterativeAppConfig
from enum import Enum

class ProjectFile(str, Enum):
    ACTION_POSTFIX = "_actions.py"
    

class ProjectFolder(str, Enum):
    SERVICE = "service"
    MODELS = "models"
    ACTIONS = "actions"
    CONFIG = "config"
    DOCS = "docs"
    TESTS = "tests"
    STREAMLITS = "streamlits"
    DATA = "data"
    

class Project(IterativeModel):
    root_path: Optional[str] = Field(None)
    config: Optional[IterativeAppConfig] = Field(None)
    models: Optional[dict] = Field(None)
    services: Optional[dict] = Field(None)
    actions: Optional[dict] = Field(None)