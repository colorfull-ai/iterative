import ast
import os
import textwrap
import humps
from logging import getLogger as _getLogger
from iterative.config import get_config as _get_config
from iterative.service.utils.project_utils import (
    get_last_project_root as _get_last_project_root,
    create_project_path as _create_project_path,
    get_project_root as _get_project_root,
)
from textwrap import dedent as _dedent


logger = _getLogger(__name__)


def _generate_crud_endpoints(class_name, model_file_path):
    class_name_snake = humps.depascalize(class_name)  # snake_case

    # Get the last and current project roots
    last_project_root = _get_last_project_root()
    current_project_root = _get_project_root()
    if last_project_root is None or current_project_root is None:
        raise Exception("No parent '.iterative' project found.")

    # Construct the relative import path from the last project root to the model file path
    model_relative_path = os.path.relpath(
        model_file_path, last_project_root
    ).replace(os.sep, ".")

    # Get the last part of the last_project_root (which is the project's name)
    last_project_name = os.path.basename(last_project_root)

    # Prepend the project's name to the model_relative_path
    model_relative_path = f"{last_project_name}.{model_relative_path}"

    # Remove the '.py' extension from the import path
    model_relative_path = model_relative_path.rsplit('.', 1)[0]

    print(f"model_relative_path: {model_relative_path}")

    return textwrap.dedent(
        f"""
    from typing import List, Optional
    from fastapi import APIRouter, HTTPException, Query
    from {model_relative_path} import {class_name}

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
    models_path = _create_project_path(_get_config().get("model_generation_path"))
    api_path = _create_project_path(_get_config().get("api_generation_path"))

    if not os.path.exists(models_path):
        print(f"Models directory {models_path} does not exist.")
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
                        print(f"Syntax error in file: {file_path}")
                        continue
        if model_found:
            break

    if not model_found:
        print(f"Model {model_name_pascal} not found in any file under {models_path}.")
        return

    # Generate CRUD endpoint script
    endpoints_script = _generate_crud_endpoints(model_name_pascal, model_file_path)
    endpoints_file_path = os.path.join(
        api_path, f"{humps.decamelize(model_name)}_api.py"
    )

    with open(endpoints_file_path, "w") as file:
        file.write(_dedent(endpoints_script))

    print(f"CRUD endpoints for {model_name} created at {endpoints_file_path}")


def fetch_web_api_routes():
    from iterative import web_app

    routes = []
    for route in web_app.routes:
        routes.append(route.path)
    print("\n".join(routes))
    return routes
