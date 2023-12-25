# doc_utils.py

import errno
import os
import yaml
from .project_utils import find_all_iterative_projects, get_project_root

def find_docs_in_project(project_path: str) -> list:
    """
    Find all markdown files in the "docs" folder of a given project.

    Args:
        project_path (str): The project directory path to search for docs.

    Returns:
        list: A list of paths to markdown files.
    """
    docs_list = []
    docs_path = os.path.join(project_path, 'docs')
    if os.path.exists(docs_path):
        for root, dirs, files in os.walk(docs_path):
            for file in files:
                if file.endswith('.md'):
                    docs_list.append(os.path.relpath(os.path.join(root, file), project_path))
    return docs_list

def generate_mkdocs_nav(docs_list: list, project_root: str) -> list:
    """
    Generate the navigation structure for the mkdocs.yml configuration.

    Args:
        docs_list (list): A list of paths to markdown files.
        project_root (str): The root path of the current project.

    Returns:
        list: A list representing the MkDocs navigation structure.
    """
    nav = []
    for doc in docs_list:
        parts = doc.split(os.sep)
        title = os.path.splitext(parts[-1])[0].replace('_', ' ').capitalize()
        # Generate relative paths for the MkDocs navigation
        # Remove the 'docs/' prefix since it's already set in 'docs_dir'
        doc_path = os.path.relpath(os.path.join(project_root, doc), os.path.join(project_root, 'docs'))
        nav.append({title: doc_path})
    return nav

def create_mkdocs_config(project_path: str, site_name: str, nav: list):
    """
    Create the mkdocs.yml configuration file in the project's .iterative folder.

    Args:
        project_path (str): The path to the project.
        site_name (str): The site name for the MkDocs site.
        nav (list): The navigation structure for the MkDocs site.
    """
    config = {
        'site_name': site_name,
        'theme': {
            'name': 'material'
        },
        'docs_dir': os.path.join(project_path, 'docs'),  # Set the correct path to the docs directory
        'nav': nav
    }
    iterative_dir = os.path.join(project_path, '.iterative')
    os.makedirs(iterative_dir, exist_ok=True)  # Ensure the directory exists
    mkdocs_yml_path = os.path.join(iterative_dir, 'mkdocs.yml')

    with open(mkdocs_yml_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def update_mkdocs_config_for_project(project_path: str):
    """
    Update the mkdocs.yml configuration for a single iterative project.

    Args:
        project_path (str): The path to the project.
    """
    docs_list = find_docs_in_project(project_path)
    if docs_list:
        # Generate navigation without the 'docs/' prefix
        nav = generate_mkdocs_nav(docs_list, project_path)
        project_name = os.path.basename(project_path)
        site_name = f"{project_name} Documentation"
        create_mkdocs_config(project_path, site_name, nav)

def update_all_mkdocs_configs(start_path: str):
    """
    Update the mkdocs.yml configuration for all iterative projects within the start path,
    and combine them into the mkdocs.yml for the root project.

    Args:
        start_path (str): The starting directory path to search for iterative projects.
    """
    root_project_path = get_project_root(start_path)
    all_navs = []

    iterative_projects = find_all_iterative_projects(start_path)
    print(f"found {len(iterative_projects)} iterative projects")
    for project_path in iterative_projects:
        print(f"found project: {project_path}")
        update_mkdocs_config_for_project(project_path)
        docs_list = find_docs_in_project(project_path)
        if docs_list:
            nav = generate_mkdocs_nav(docs_list, project_path)
            all_navs.extend(nav)

    # Now create or update the mkdocs.yml for the root project
    if root_project_path:
        root_site_name = os.path.basename(root_project_path) + " Documentation"
        create_mkdocs_config(root_project_path, root_site_name, all_navs)


