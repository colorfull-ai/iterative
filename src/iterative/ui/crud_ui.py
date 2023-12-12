import json
import os
import sys
from fastapi import APIRouter
from iterative.api_processing import get_model_router
from iterative.config import get_config
import streamlit as st
import requests
from fastapi.routing import APIRoute
import importlib
from typing import Type, Optional
from pydantic import BaseModel

API_BASE_URL = f"http://{get_config().get('fastapi_host')}:{get_config().get('fastapi_port')}"

def get_model_by_route(route: APIRoute) -> Optional[Type[BaseModel]]:
    for dep in route.dependencies:
        if isinstance(dep.dependency, Type) and issubclass(dep.dependency, BaseModel):
            # Return the first BaseModel subclass found
            return dep.dependency
    return None

def create_form(model: Type[BaseModel]):
    values = {}
    for field, field_type in model.__annotations__.items():
        # Here you might want to handle different field types differently
        values[field] = st.text_input(f"{field} ({field_type})", "")
    return values

def main():
    st.title("Iterative CRUD UI")
    if len(sys.argv) < 2:
        st.error("No model name file provided.")
        return

    model_name_file = sys.argv[1]
    try:
        with open(model_name_file, 'r') as file:
            data = json.load(file)
            model_name = data.get('model_name', '')
    except Exception as e:
        st.error(f"Error reading model name file: {e}")
        return

    if not model_name:
        st.error("Model name not found in the provided file.")
        return
    
    router = get_model_router(model_name.lower())
    
    # Iterate over each route in the router to find corresponding Pydantic models
    for route in router.routes:
        if isinstance(route, APIRoute):
            model = get_model_by_route(route)
            if model and model.__name__.lower() == model_name.lower():
                # Generate the UI based on the model
                st.title(f"CRUD Operations for {model.__name__}")

                if 'post' in route.methods:
                    # Create operation
                    create_values = create_form(model)
                    if st.button("Create"):
                        response = requests.post(f"{API_BASE_URL}{route.path}", json=create_values)
                        st.json(response.json())
                elif 'get' in route.methods:
                    # Read operation
                    get_id = st.text_input("Enter ID to retrieve", key=f"{model_name}_get")
                    if st.button("Get"):
                        response = requests.get(f"{API_BASE_URL}{route.path}/{get_id}")
                        st.json(response.json())
                elif 'put' in route.methods:
                    # Update operation
                    update_id = st.text_input("Enter ID to update", key=f"{model_name}_update")
                    update_values = create_form(model)
                    if st.button("Update"):
                        response = requests.put(f"{API_BASE_URL}{route.path}/{update_id}", json=update_values)
                        st.json(response.json())
                elif 'delete' in route.methods:
                    # Delete operation
                    delete_id = st.text_input("Enter ID to delete", key=f"{model_name}_delete")
                    if st.button("Delete"):
                        response = requests.delete(f"{API_BASE_URL}{route.path}/{delete_id}")
                        st.json(response.json())


if __name__ == "__main__":
    main()