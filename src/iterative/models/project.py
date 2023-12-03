from __future__ import annotations

from iterative.models.config import IterativeAppConfig
from pydantic import BaseModel
import yaml

class File(BaseModel):
    name: str
    path: str
    file_type: str  # e.g., '.py', '.js', '.json', etc.
    size: int       # in bytes

class Directory(BaseModel):
    name: str
    path: str
    files: list[File]
    subdirectories: list['Directory']  # List of subdirectories

class Configuration(BaseModel):
    config_type: str   # e.g., 'docker', 'webpack', 'database'
    settings: dict     # Key-value pairs for configuration settings



class Project(BaseModel):
    name: str
    root_directory: Directory
    configurations: list[Configuration]
    subprojects: list[Project]
    iterative_app_config: IterativeAppConfig

    def __init__(self, name, root_directory):
        self.name = name
        self.root_directory = root_directory
        self.configurations = []
        self.subprojects = []
        self.iterative_app_config = None
        self.discover_subprojects(root_directory)
        self.load_iterative_app_config(root_directory)

    def discover_subprojects(self, directory):
        for subdir in directory.subdirectories:
            if self.is_subproject(subdir):
                new_project = Project(name=subdir.name, root_directory=subdir)
                self.subprojects.append(new_project)
            self.discover_subprojects(subdir)

    def is_subproject(self, directory):
        # Implement logic to determine if a directory is a separate project
        pass

    def load_iterative_app_config(self, directory):
        config_path = self.find_config_file(directory)
        if config_path:
            self.iterative_app_config = IterativeAppConfig.load_from_file(config_path)

    def find_config_file(self, directory):
        # Implement logic to locate the Iterative app config file
        # For example, searching for a specific filename
        pass
