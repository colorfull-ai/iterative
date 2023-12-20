from iterative.service.utils.service_utils import ( 
                                                    find_project_service_functions_in_cwd, 
                                                    find_project_service_functions_in_iterative_project,
                                                    find_project_service_functions_in_parent_project
                                                    )
import pytest

@pytest.mark.parametrize("function_finder,expected_function_name,expected_file_name", [
    (find_project_service_functions_in_cwd, 'find_project_service_functions', 'service_utils.py'),
    (find_project_service_functions_in_iterative_project, 'find_project_service_functions', 'service_utils.py'),
    (find_project_service_functions_in_parent_project, 'find_project_service_functions', 'service_utils.py')
])
def test_function_finder(function_finder, expected_function_name, expected_file_name):
    functions = function_finder()
    assert expected_function_name in functions
    assert functions[expected_function_name]["file_path"].endswith(expected_file_name)