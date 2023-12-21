from iterative.service.utils.service_utils import ( 
                                                    find_project_service_functions_in_iterative_project,
                                                    find_project_service_functions_in_parent_project
                                                    )
import pytest

@pytest.mark.parametrize("function_finder,expected_function_name", [
    (find_project_service_functions_in_iterative_project, 'find_project_service_functions'),
    (find_project_service_functions_in_parent_project, 'find_project_service_functions')
])
def test_function_finder(function_finder, expected_function_name):
    functions = function_finder()
    # project name is the key, with a list of function dictionaries as the value
    # get function names of all function_names
    # need to flatten the list of dictionaries and get the names
    function_names = [function["function_name"] for function_list in functions.values() for function in function_list]

    assert expected_function_name in function_names