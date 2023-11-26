import ast
import os
import textwrap
import humps

class ClassFinder(ast.NodeVisitor):
    def __init__(self):
        self.classes = []

    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'BaseFirebaseModel':
                self.classes.append(node.name)
        self.generic_visit(node)

def _generate_crud_endpoints(class_name):
    class_name_camel = humps.camelize(class_name)  # CamelCase
    class_name_snake = humps.decamelize(class_name)  # snake_case

    return textwrap.dedent(f"""
    from typing import List, Optional
    from fastapi import APIRouter, HTTPException, Query
    from firebase_admin import firestore
    from db_models import {class_name_camel}

    db = firestore.client()
    router = APIRouter()

    @router.post("/{class_name_snake}s")
    async def create_{class_name_snake}({class_name_snake}_data: {class_name}):
        if {class_name}.get_by_id({class_name_snake}_data.id):
            raise HTTPException(status_code=409, detail="{class_name_camel} already exists")
        
        {class_name_snake}_data.save()
        return {class_name_snake}_data

    @router.get("/{class_name_snake}s/{{{class_name_snake}_id}}")
    async def get_{class_name_snake}({class_name_snake}_id: str):
        {class_name_snake} = {class_name}.get_by_id({class_name_snake}_id)
        if not {class_name_snake}:
            raise HTTPException(status_code=404, detail="{class_name_camel} not found")
        return {class_name_snake}

    @router.put("/{class_name_snake}s/{{{class_name_snake}_id}}")
    async def update_{class_name_snake}({class_name_snake}_id: str, {class_name_snake}_update: {class_name}):
        existing_{class_name_snake} = {class_name}.get_by_id({class_name_snake}_id)
        if not existing_{class_name_snake}:
            raise HTTPException(status_code=404, detail="{class_name_camel} not found")
        existing_{class_name_snake}.merge({class_name_snake}_update.json())
        existing_{class_name_snake}.save()
        return existing_{class_name_snake}

    @router.delete("/{class_name_snake}s/{{{class_name_snake}_id}}")
    async def delete_{class_name_snake}({class_name_snake}_id: str):
        {class_name_snake} = {class_name}.get_by_id({class_name_snake}_id)
        if not {class_name_snake}:
            raise HTTPException(status_code=404, detail="{class_name_camel} not found")
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
            raise HTTPException(status_code=404, detail="{class_name_camel}s not found")
        return {class_name_snake}s
    """)


def process_script(script_path: str, output_dir: str):
    """
    Process a script to find classes inheriting from BaseFirebaseModel and generate CRUD endpoints.

    :param script_path: Path to the script to be processed.
    :param output_dir: Directory where the generated CRUD endpoint scripts will be saved.
    """
    with open(script_path, "r") as file:
        source = file.read()

    tree = ast.parse(source)
    finder = ClassFinder()
    finder.visit(tree)

    os.makedirs(output_dir, exist_ok=True)

    for class_name in finder.classes:
        endpoints_script = _generate_crud_endpoints(class_name)
        file_path = os.path.join(output_dir, f"{humps.decamelize(class_name).lower()}_endpoints.py")
        with open(file_path, "w") as file:
            file.write(endpoints_script)
        print(f"CRUD Endpoints for {class_name} generated at: {file_path}")