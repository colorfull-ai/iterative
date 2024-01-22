from collections import defaultdict
import ast
import os
import inspect
import textwrap
from typing import Dict
import humps
import yaml
from fastapi import APIRouter
from iterative.service.project_management.service.project_utils import get_parent_project_root, get_project_root, is_iterative_project, load_module_from_path
from logging import getLogger
from iterative.config import get_config as _get_config
from iterative.service.project_management.service.project_utils import (
    get_parent_project_root as _get_parent_project_root,
    resolve_project_folder_path as _resolve_project_folder_path,
    get_project_root as _get_project_root,
)
from textwrap import dedent as _dedent


logger = getLogger(__name__)

def read_api_path_from_config(config_path: str) -> str:
    """
    Reads the API path from the project's configuration file.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        return config.get('api_generation_path', 'api') if config else 'api'

def find_api_routers_from_path(start_path: str, file_name: str = None):
    """
    Searches for FastAPI routers in the specified start path and its 'service' directories.
    Checks the start path for an 'api' directory and then recursively searches in 'service' directories.
    Only considers directories that are identified as iterative projects.
    """
    routers_dict = defaultdict(list)

    def add_routers_from_path(search_path):
        for root, _, files in os.walk(search_path):
            for file in files:
                if file.endswith(".py") and (not file_name or file == file_name):
                    full_path = os.path.join(root, file)
                    module = load_module_from_path(full_path)
                    project_path = get_project_root(root)
                    project_name = os.path.basename(project_path)

                    for _, obj in inspect.getmembers(module):
                        if isinstance(obj, APIRouter):
                            # Check if the router has tags, if not, add a default tag
                            obj.tags = [f'{project_name}']
                            routers_dict[project_name].append({
                                "file_path": full_path,
                                "project_name": project_name,
                                "router": obj,
                                "router_name": "Unnamed router"
                            })

    def search_iterative_projects_in_service_dirs(root_path):
        if is_iterative_project(root_path):
            api_folder = os.path.join(root_path, 'api')
            if os.path.exists(api_folder):
                add_routers_from_path(api_folder)

        for root, dirs, _ in os.walk(root_path):
            if 'service' in root.split(os.sep):  # Checking if 'service' is in the path
                for dir in dirs:
                    service_dir_path = os.path.join(root, dir)
                    if is_iterative_project(service_dir_path):
                        api_folder = os.path.join(service_dir_path, 'api')
                        if os.path.exists(api_folder):
                            add_routers_from_path(api_folder)

    search_iterative_projects_in_service_dirs(start_path)
    return routers_dict


def find_api_routers_in_iterative_project():
    project_root = get_project_root()
    logger.info(f"Project root: {project_root}")
    if project_root:
        return find_api_routers_from_path(project_root)
    else:
        print("No .iterative project found in the current directory tree.")
        return {}
    

def find_api_routers_in_parent_project():
    parent_project_root = get_parent_project_root()
    logger.info(f"Parent project root: {parent_project_root}")
    if parent_project_root:
        return find_api_routers_from_path(parent_project_root)
    else:
        logger.warning("No .iterative project found in the current directory tree.")
        return {}


def get_model_router(model_name: str):
    """
    Finds FastAPI routers in the project, filtering by a specified model name.

    Args:
        model_name (str): The name of the model to find the router for.

    Returns:
        List[APIRouter]: A list of FastAPI routers related to the specified model.
    """
    iterative_root = os.getcwd()
    target_file_name = f"{model_name.lower()}_api.py"  # File name pattern

    for root, dirs, _ in os.walk(iterative_root):
        if '.iterative' in dirs:
            config_path = os.path.join(root, '.iterative', 'config.yaml')
            if not os.path.exists(config_path):
                continue

            api_path = read_api_path_from_config(config_path)
            full_api_path = os.path.join(root, api_path)
            if os.path.exists(full_api_path):
                # Filter routers by the target file name
                for router in find_api_routers_from_path(full_api_path, target_file_name):
                    print(f"Found router: {router}")
                    return router
                
def fetch_web_api_routes():
    from iterative import web_app

    routes = []
    for route in web_app.routes:
        routes.append(route.path)
    logger.info("\n".join(routes))
    return routes



def generate_crud_endpoints(class_name, model_file_path):
    class_name_snake = humps.depascalize(class_name)  # snake_case

    # Get the last and current project roots
    parent_project_root = _get_parent_project_root()
    current_project_root = _get_project_root()
    if parent_project_root is None or current_project_root is None:
        raise Exception("No parent '.iterative' project found.")

    relative_path_from_parent_to_model = create_relative_import_path(model_file_path, parent_project_root)


    return textwrap.dedent(
        f"""
    from typing import List, Optional
    from fastapi import APIRouter, HTTPException, Query
    from {relative_path_from_parent_to_model} import {class_name}

    router = APIRouter()

    @router.post("/{class_name_snake}s")
    async def create_{class_name_snake}({class_name_snake}_data: {class_name}):
        if {class_name}.get_by_id({class_name_snake}_data.id):
            raise HTTPException(status_code=409, detail="{class_name} already exists")
        
        {class_name_snake}_data.save()
        return {class_name_snake}_data

    @router.get("/{class_name_snake}s/{{{class_name_snake}_id}}")
    async def get_{class_name_snake}({class_name_snake}_id: str):
        {class_name_snake} = {class_name}.get_by_id({class_name_snake}_id)
        if not {class_name_snake}:
            raise HTTPException(status_code=404, detail="{class_name} not found")
        return {class_name_snake}

    @router.put("/{class_name_snake}s/{{{class_name_snake}_id}}")
    async def update_{class_name_snake}({class_name_snake}_id: str, {class_name_snake}_update: {class_name}):
        existing_{class_name_snake} = {class_name}.get_by_id({class_name_snake}_id)
        if not existing_{class_name_snake}:
            raise HTTPException(status_code=404, detail="{class_name} not found")
        existing_{class_name_snake}.merge({class_name_snake}_update.json())
        existing_{class_name_snake}.save()
        return existing_{class_name_snake}

    @router.delete("/{class_name_snake}s/{{{class_name_snake}_id}}")
    async def delete_{class_name_snake}({class_name_snake}_id: str):
        {class_name_snake} = {class_name}.get_by_id({class_name_snake}_id)
        if not {class_name_snake}:
            raise HTTPException(status_code=404, detail="{class_name} not found")
        {class_name_snake}.delete()
        return {class_name_snake}

    @router.get("/{class_name_snake}s", response_model=List[{class_name}])
    async def get_{class_name_snake}s(
        page: int = Query(1, alias="page", description="Page number to retrieve"),
        page_size: int = Query(10, alias="page_size", description="Number of items per page", gt=0, le=100),
        # Add other filtering parameters as needed
    ):
        query_params = {{}}
        # Add logic to process filtering parameters and add to query_params

        {class_name_snake}s = {class_name}.get_page(page=page, page_size=page_size, query_params=query_params)
        if not {class_name_snake}s:
            raise HTTPException(status_code=404, detail="{class_name}s not found")
        return {class_name_snake}s
    """
    )


def generate_endpoints_for_model(model_name: str):
    model_name_pascal = humps.pascalize(model_name)
    models_path = _resolve_project_folder_path(_get_config().get("model_generation_path"))
    api_path = _resolve_project_folder_path(_get_config().get("api_generation_path"))

    if not os.path.exists(models_path):
        logger.info(f"Models directory {models_path} does not exist.")
        return

    os.makedirs(api_path, exist_ok=True)

    # New logic to search for the model in all Python files
    model_found = False
    model_file_path = None
    for root, dirs, files in os.walk(models_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    try:
                        tree = ast.parse(file_content)
                        for node in ast.walk(tree):
                            if (
                                isinstance(node, ast.ClassDef)
                                and node.name == model_name_pascal
                            ):
                                model_found = True
                                model_file_path = file_path
                                break
                    except SyntaxError:
                        logger.error(f"Syntax error in file: {file_path}")
                        continue
        if model_found:
            break

    if not model_found:
        logger.error(f"Model {model_name_pascal} not found in any file under {models_path}.")
        return

    # Generate CRUD endpoint script
    endpoints_script = generate_crud_endpoints(model_name_pascal, model_file_path)
    endpoints_file_path = os.path.join(
        api_path, f"{humps.decamelize(model_name)}_api.py"
    )

    with open(endpoints_file_path, "w") as file:
        file.write(_dedent(endpoints_script))

    logger.info(f"CRUD endpoints for {model_name} created at {endpoints_file_path}")

def get_openapi_schema() -> Dict:
    """
    Fetch the OpenAPI schema from the FastAPI application.

    Returns:
    dict: The OpenAPI schema as a dictionary.
    """
    from iterative import web_app

    logger.info("Fetching OpenAPI schema from FastAPI application")
    logger.debug(web_app.openapi())

    return web_app.openapi()
