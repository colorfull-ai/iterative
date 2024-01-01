
from iterative.service.utils.api_utils import find_api_routers_in_iterative_project, find_api_routers_in_parent_project, find_api_routers_in_parent_project
import pytest

@pytest.mark.parametrize("router_finder,expected_endpoint,expected_file_name", [
    (find_api_routers_in_iterative_project, '/health', 'health.py'),
    (find_api_routers_in_parent_project, '/health', 'health.py'),
    (find_api_routers_in_parent_project, '/health', 'health.py')
])
def test_router_finder(router_finder, expected_endpoint, expected_file_name):
    routers_dict = router_finder()

    routers = [router_dict["router"] for router_list in routers_dict.values() for router_dict in router_list]
    # fast api router endpoint
    router_paths = [route.path for router in routers for route in router.routes]
    assert expected_endpoint in router_paths

    # check that the router is in the correct file, split the file path to the file name
    file_names = [router_dict["file_path"].split('/')[-1] for router_list in routers_dict.values() for router_dict in router_list]
    assert expected_file_name in file_names