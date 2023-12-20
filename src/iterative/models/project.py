from iterative.models.config import IterativeAppConfig
from iterative.models.iterative import IterativeModel


class Project(IterativeModel):
    root_path: str
    config: IterativeAppConfig
    models: dict
    service: dict
    actions: dict
    
