import os
from iterative.service.utils.model_utils import execute_python_code_isolated, find_models_in_config_path, find_models_in_cwd

def test_find_models_in_cwd():
    models = find_models_in_cwd()
    assert isinstance(models, dict)
    print(models.keys())
    assert os.path.basename(models['action.Action']) == 'action.py'
    for model_path in models.values():
        assert os.path.exists(model_path)

def test_find_models_in_config_path():
    models = find_models_in_config_path()
    assert isinstance(models, dict)
    for model_path in models.values():
        assert os.path.exists(model_path)

def test_read_model_files():
    # {model_name: model_path}
    models = find_models_in_config_path()
    for model_path in models.values():
        with open(model_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            assert len(file_content) > 0

def test_read_model_file():
    models = find_models_in_config_path()
    model_path = models['action.Action']
    with open(model_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        assert len(file_content) > 0


def test_execute_python_code_isolated():
    # Define some Python code to execute
    code = """
    from iterative.service.utils.model_utils import find_models_in_cwd
    models = find_models_in_cwd()
    """

    # Execute the code
    module = execute_python_code_isolated(code)

    # Check that the module has a 'models' variable
    assert isinstance(module.models, dict)
    assert 'action.Action' in module.models

def test_execute_python_code_isolated_exception():
    # Define some Python code that raises an exception
    code = """
    raise ValueError("Test error")
    """

    # Execute the code
    result = execute_python_code_isolated(code)

    # Check that the result is a traceback string
    assert isinstance(result, str)
    assert "ValueError: Test error" in result