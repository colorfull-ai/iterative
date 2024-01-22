import pytest
import yaml
from iterative.service.utils import doc_utils

# Define the markdown files to be created for testing
markdown_files = [
    'ai_action_system.md',
    'ai_iterative_assistant_chain_scenario.md',
    'api_errors.md',
    'example_goal.md',
    'execute_action_calls.md',
    'frontend_nextjs_project_structure.md',
    'index.md',
    'iter_agent_assistant_prompt.md',
    'iter_agent_game_prompt.md',
    'nosql_yorm.md',
    'unit_tests_doc.md'
]

@pytest.fixture
def project_structure(tmp_path):
    # Create a docs directory
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()

    # Create markdown files in the docs directory
    for file_name in markdown_files:
        file_path = docs_dir / file_name
        file_path.write_text(f"# {file_name}\nContent for {file_name}")

    # Return the path to the project (tmp_path in this case)
    return tmp_path

def test_find_docs_in_project(project_structure):
    docs_list = doc_utils.find_docs_in_project(str(project_structure))
    assert len(docs_list) == len(markdown_files)

def test_generate_mkdocs_nav(project_structure):
    docs_list = doc_utils.find_docs_in_project(str(project_structure))
    nav = doc_utils.generate_mkdocs_nav(docs_list, str(project_structure))
    assert len(nav) == len(markdown_files)

# def test_create_mkdocs_config(project_structure):
#     nav = [{'Index': 'docs/index.md'}, {'About': 'docs/about.md'}]
#     site_name = 'Test Documentation'
#     doc_utils.create_mkdocs_config(str(project_structure), site_name, nav)

#     mkdocs_yml_path = project_structure / '.iterative' / 'mkdocs.yml'
#     assert mkdocs_yml_path.exists()

#     # Read the contents of the generated mkdocs.yml file
#     with open(mkdocs_yml_path, 'r') as f:
#         contents = f.read()

#     # Check if the site name is in the contents
#     assert site_name in contents
#     # Check if the nav structure is in the contents
#     for item in nav:
#         for title, path in item.items():
#             assert title in contents
#             assert path in contents

def test_create_mkdocs_config(project_structure):
    nav = [{'Index': 'docs/index.md'}, {'About': 'docs/about.md'}]
    site_name = 'Test Documentation'
    doc_utils.create_mkdocs_config(str(project_structure), site_name, nav)

    mkdocs_yml_path = project_structure / '.iterative' / 'mkdocs.yml'
    assert mkdocs_yml_path.exists()

    # Read the contents of the generated mkdocs.yml file
    with open(mkdocs_yml_path, 'r') as f:
        contents = f.read()

    # Parse the YAML content
    mkdocs_config = yaml.safe_load(contents)

    # Check if the site name is in the contents
    assert mkdocs_config['site_name'] == site_name
    # Check if the nav structure is in the contents
    assert mkdocs_config['nav'] == nav