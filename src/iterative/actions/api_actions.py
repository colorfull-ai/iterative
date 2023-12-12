import os
import textwrap
import humps
from logging import getLogger as _getLogger
from iterative.config import get_config as _get_config
from textwrap import dedent as _dedent

from iterative.utils import create_project_path as _create_project_path

logger = _getLogger(__name__)

def _generate_crud_endpoints(class_name):
    class_name_snake = humps.decamelize(class_name)  # snake_case
    class_name_snake = humps.depascalize(class_name_snake)  # snake_case

    return textwrap.dedent(f"""
    from typing import List, Optional
    from fastapi import APIRouter, HTTPException, Query
    from models.{class_name_snake} import {class_name}

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
    """)



def generate_endpoints_for_model(model_name: str):
    """
    Generate FastAPI CRUD endpoints for a given model and save them in the 'endpoints' directory.

    """
    model_name_pascal = humps.pascalize(model_name)
    models_path = _create_project_path(_get_config().get("model_generation_path"))
    api_path = _create_project_path(_get_config().get("api_generation_path"))

    # Ensure the 'models' directory exists
    if not os.path.exists(models_path):
        print(f"Models directory {models_path} does not exist.")
        return
    
    os.makedirs(api_path, exist_ok=True)

    model_file_name = f"{model_name_pascal}.py"
    model_file_path = os.path.join(models_path, model_file_name)

    # Ensure the model file exists
    if not os.path.isfile(model_file_path):
        print(f"Model file {model_file_path} does not exist.")
        return

    # Generate CRUD endpoint script
    endpoints_script = _generate_crud_endpoints(model_name_pascal)
    endpoints_file_path = os.path.join(api_path, f"{humps.decamelize(model_name)}_api.py")

    # Write the endpoints to the file, overwriting any existing file
    with open(endpoints_file_path, 'w') as file:
        file.write(_dedent(endpoints_script))

    print(f"CRUD endpoints for {model_name} created at {endpoints_file_path}")


def fetch_web_api_routes():
    from iterative import web_app

    routes = []
    for route in web_app.routes:
        routes.append(route.path)
    print('\n'.join(routes))
    return routes