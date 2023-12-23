from iterative.actions.api_actions import create_relative_import_path
import pytest

def test_create_relative_import_path():
    model_file_path = "/home/user/project/subproject/models/model.py"
    parent_project_root = "/home/user/project"
    expected_relative_import_path = "project.subproject.models.model"

    assert create_relative_import_path(model_file_path, parent_project_root) == expected_relative_import_path

def test_create_relative_import_path_nested():
    model_file_path = "/home/user/project/subproject/services/service/models/model.py"
    parent_project_root = "/home/user/project"
    expected_relative_import_path = "project.subproject.services.service.models.model"

    assert create_relative_import_path(model_file_path, parent_project_root) == expected_relative_import_path

def test_create_relative_import_path_same_directory():
    model_file_path = "/home/user/project/model.py"
    parent_project_root = "/home/user/project"
    expected_relative_import_path = "project.model"

    assert create_relative_import_path(model_file_path, parent_project_root) == expected_relative_import_path