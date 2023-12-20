from enum import Enum


class ProjectFolder(str, Enum):
    SERVICE = "service"
    MODELS = "models"
    ACTIONS = "actions"
    CONFIG = "config"
    DOCS = "docs"
    TESTS = "tests"
    STREAMLITS = "streamlits"
    DATA = "data"
    