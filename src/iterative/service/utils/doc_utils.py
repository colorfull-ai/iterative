# doc_utils.py

import errno
import os
import shutil
import yaml
from .project_utils import find_all_iterative_projects, get_project_name, get_project_root

def find_docs_in_project(project_path: str, root: bool=False) -> list:
    """
    Find all markdown files in the "docs" folder of a given project, including
    any nested folders under the 'service' directory that contains a '.iterative' directory.

    Args:
        project_path (str): The project directory path to search for docs.

    Returns:
        list: A list of paths to markdown files.
    """
    docs_list = []

    if root:
        # Search for markdown files in the 'docs' directory
        docs_path = os.path.join(get_project_root(project_path), 'docs')
        for root, dirs, files in os.walk(docs_path):
            for file in files:
                if file.endswith('.md'):
                    docs_list.append(os.path.relpath(os.path.join(root, file), project_path))
    
    # Search for markdown files in the 'service' directory
    service_path = os.path.join(get_project_root(project_path), 'service')
    for root, dirs, files in os.walk(service_path):
        if '.iterative' in dirs:
            docs_subdir = os.path.join(get_project_root(root), 'docs')
            if os.path.exists(docs_subdir):
                for file in os.listdir(docs_subdir):
                    if file.endswith('.md'):
                        docs_list.append(os.path.relpath(os.path.join(docs_subdir, file), project_path))
    return docs_list

def generate_mkdocs_nav(build_dir: str) -> list:
    """
    Generate the navigation structure for the mkdocs.yml configuration,
    sectioned by 'docs' and 'service'.

    Args:
        build_dir (str): The build directory where the markdown files are located.

    Returns:
        list: A list representing the MkDocs navigation structure.
    """
    project_name = get_project_name(get_project_root())
    nav_project_key = f"{project_name.replace('_', ' ').title()} Docs"
    nav = {nav_project_key: []}
    service_nav = {}

    # Process each documentation file
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            if file.endswith('.md'):
                doc_path = os.path.relpath(os.path.join(root, file), build_dir)
                title = os.path.splitext(file)[0].replace('_', ' ').capitalize()
                # Determine if the doc is under 'docs' or 'service'
                if root.startswith(os.path.join(build_dir, 'docs')):
                    # This is a 'docs' document
                    nav[nav_project_key].append({title: doc_path})
                elif 'service' in root.split(os.sep):
                    # This is a 'service' document
                    service_parts = root.split(os.sep)
                    service_name = service_parts[service_parts.index('service') + 1]
                    service_name = service_name.replace('_', ' ').title()
                    if service_name not in service_nav:
                        service_nav[service_name] = []
                    service_nav[service_name].append({title: doc_path})

    # Convert the service_nav dictionary to a list of dictionaries for MkDocs compatibility
    for service, items in service_nav.items():
        nav[service] = items

    # Convert the nav dictionary to a list for MkDocs compatibility
    nav_list = []
    for section, items in nav.items():
        if items:  # Only add sections that have items
            nav_list.append({section: items})

    return nav_list

def create_mkdocs_config(project_path: str, site_name: str, nav: dict):
    """
    Create the mkdocs.yml configuration file in the project's .iterative folder.

    Args:
        project_path (str): The path to the project.
        site_name (str): The site name for the MkDocs site.
        nav (dict): The navigation structure for the MkDocs site.
    """
    config = {
        'site_name': site_name,
        'theme': {
            'name': 'material',
            'custom_dir': 'overrides'
        },
        'docs_dir': '../docs/build',  # Corrected relative path to the build directory
        'nav': nav
    }

    # Ensure the .iterative directory exists
    iterative_dir = os.path.join(project_path, '.iterative')
    os.makedirs(iterative_dir, exist_ok=True)

    # Ensure the overrides directory exists
    overrides_dir = os.path.join(iterative_dir, 'overrides')
    os.makedirs(overrides_dir, exist_ok=True)

    # Path to the mkdocs.yml file
    mkdocs_yml_path = os.path.join(iterative_dir, 'mkdocs.yml')

    # Write the mkdocs.yml configuration file
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
        nav = generate_mkdocs_nav(docs_list, get_project_root(project_path))
        project_name = os.path.basename(project_path)
        site_name = f"{project_name} Documentation"
        create_mkdocs_config(project_path, site_name, nav)

def update_all_mkdocs_configs(start_path: str):
    """
    Update the mkdocs.yml configuration for all iterative projects within the start path.
    This will delete the existing 'build' directory under 'docs', create a new one,
    copy all markdown files into it, and update the mkdocs.yml configuration to reference
    these files in the navigation.

    Args:
        start_path (str): The starting directory path to search for iterative projects.
    """
    root_project_path = get_project_root(start_path)
    build_dir = os.path.join(root_project_path, 'docs', 'build')

    # Delete the build directory if it exists
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    # Ensure the build directory exists
    os.makedirs(build_dir, exist_ok=True)

    all_docs = []
    iterative_projects = find_all_iterative_projects(start_path)
    root_docs_list = find_docs_in_project(root_project_path, root=True)
    copy_docs_to_build_dir(root_docs_list, root_project_path, build_dir, os.path.basename(root_project_path))

    # Copy all markdown files from each project's docs to the build directory
    for project_path in iterative_projects[1:]:
        project_name = os.path.basename(project_path)
        docs_list = find_docs_in_project(project_path)
        all_docs.extend(docs_list)
        # paths and dir
        copy_docs_to_build_dir(docs_list, get_project_root(project_path), build_dir, project_name)

    # Generate navigation for all docs in the build directory
    nav = generate_mkdocs_nav(build_dir)
    root_site_name = os.path.basename(root_project_path) + " Documentation"
    create_mkdocs_config(root_project_path, root_site_name, nav)

def copy_docs_to_build_dir(docs_list, project_root, build_dir, project_name):
    """
    Copy all markdown files to the build directory under the main docs folder.
    The directory structure of the source files will be maintained within their respective
    project subdirectories in the build directory.

    Args:
        docs_list (list): A list of paths to markdown files.
        project_root (str): The root path of the current project.
        build_dir (str): The build directory where files will be copied.
        project_name (str): The name of the current project.
    """
    for doc in docs_list:
        # Create the full path for the source document
        full_doc_path = os.path.join(project_root, doc)
        # Create a new path within the build directory, maintaining the original structure
        doc_relative_path = os.path.relpath(full_doc_path, project_root)
        new_doc_path = os.path.join(build_dir, doc_relative_path)
        new_doc_dir = os.path.dirname(new_doc_path)

        # Create directories if they don't exist
        os.makedirs(new_doc_dir, exist_ok=True)

        # Copy the file to the new path
        shutil.copyfile(full_doc_path, new_doc_path)