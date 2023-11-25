import os
from textwrap import dedent as _dedent
from typing import Dict, List, Optional
from iterative.config import get_config
from iterative.scripts.create_endpoints_from_models import _generate_crud_endpoints
import humps

def generate_endpoints_for_model(model_name: str, models_path: Optional[str] = None, endpoints_path: Optional[str] = None):
    """
    Generate FastAPI CRUD endpoints for a given model and save them in the 'endpoints' directory.

    Args:
        model_name (str): Name of the model for which to generate endpoints.
        models_path (Optional[str]): Path to the directory containing the model files. Defaults to the 'models' directory in the current working directory.
        endpoints_path (Optional[str]): Path to the directory where the endpoints files will be saved. Defaults to the 'endpoints' directory in the current working directory.
    """
    # Fetch paths from the global configuration if not provided
    if not models_path or not endpoints_path:
        config = get_config()
        base_path = config.get('model_generation_path', os.getcwd())
        models_path = models_path or os.path.join(base_path, 'models')
        endpoints_path = endpoints_path or os.path.join(base_path, 'endpoints')

    # Ensure the 'models' directory exists
    if not os.path.exists(models_path):
        print(f"Models directory {models_path} does not exist.")
        return
    
    # Ensure the 'endpoints' directory exists
    os.makedirs(endpoints_path, exist_ok=True)

    model_file_name = f"{humps.pascalize(model_name)}.py"
    model_file_path = os.path.join(models_path, model_file_name)

    # Ensure the model file exists
    if not os.path.isfile(model_file_path):
        print(f"Model file {model_file_path} does not exist.")
        return

    # Generate CRUD endpoint script
    endpoints_script = _generate_crud_endpoints(model_name)
    endpoints_file_path = os.path.join(endpoints_path, f"{humps.decamelize(model_name)}_endpoints.py")

    # Write the endpoints to the file, overwriting any existing file
    with open(endpoints_file_path, 'w') as file:
        file.write(_dedent(endpoints_script))

    print(f"CRUD endpoints for {model_name} created at {endpoints_file_path}")


def create_model(entity_name: str, model_generation_path: Optional[str] = None):
    """
    Create a basic nosql_yorm model file with the given entity name in a 'models' directory.

    Args:
        entity_name (str): Name of the entity for which the model is to be created.
        model_generation_path (Optional[str]): Path where the model file will be created. Defaults to the current working directory.
    """
    # Fetch the model generation path from the global configuration if not provided
    if not model_generation_path:
        config = get_config()
        model_generation_path = config.get('model_generation_path', os.getcwd())

    # Append 'models' to the model generation path to ensure the directory structure
    model_folder = os.path.join(model_generation_path, 'models')

    try:
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
    except OSError as e:
        print(f"Error creating directory {model_folder}: {e}")
        return

    # Generate the model class content
    class_name = entity_name.title().replace('_', '')
    file_name = f"{class_name}.py"
    file_path = os.path.join(model_folder, file_name)
    model_content = f"""from nosql_yorm.models import BaseFirebaseModel

class {class_name}(BaseFirebaseModel):
    _collection_name = "{class_name}"
    # TODO: Add fields here
"""

    # Write the model class to the file, overwriting any existing file
    with open(file_path, 'w') as file:
        file.write(_dedent(model_content))

    print(f"Model {class_name} created at {file_path}")


def add_property_to_model(entity_name: str, property_name: str, property_type: str, model_generation_path: str = None):
    """
    Add a new property to an existing nosql_yorm model.

    Args:
        entity_name (str): The name of the entity to which the property will be added.
        property_name (str): The name of the property to be added.
        property_type (str): The data type of the property to be added.
        model_generation_path (str, optional): The path to the directory containing the model file. Defaults to the current working directory.

    This function adds a new property to the specified model class. The property is appended to the class definition in the model's Python file.
    """
    model_folder = model_generation_path or os.getcwd()
    file_name = f"{entity_name}.py".lower()
    file_path = os.path.join(model_folder, file_name)

    if not os.path.exists(file_path):
        print(f"Model file {file_path} does not exist.")
        return

    new_property_line = f"    {property_name}: Optional[{property_type}] = None\n"

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        insert_line_index = next((i for i, line in enumerate(lines) if 'collection_name' in line), None)

        if insert_line_index is not None:
            lines.insert(insert_line_index + 1, new_property_line)
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        else:
            print(f"Collection name not found in {file_path}. Cannot add property.")

    print(f"Property {property_name} added to model {entity_name} at {file_path}")



def edit_property_in_model(entity_name: str, property_name: str, new_type: str, model_generation_path: str = None):
    """
    Edit an existing property in a nosql_yorm model.

    Args:
        entity_name (str): The name of the entity whose property will be edited.
        property_name (str): The name of the property to be edited.
        new_type (str): The new data type for the property.
        model_generation_path (str, optional): The path to the directory containing the model file. Defaults to the current working directory.

    This function modifies the data type of an existing property in the specified model class. It updates the property definition in the model's Python file.
    """

    model_folder = model_generation_path or os.getcwd()
    file_name = f"{entity_name}.py".lower()
    file_path = os.path.join(model_folder, file_name)

    if not os.path.exists(file_path):
        print(f"Model file {file_path} does not exist.")
        return

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        property_line_index = next((i for i, line in enumerate(lines) if property_name + ":" in line), None)

        if property_line_index is not None:
            lines[property_line_index] = f"{property_name}: Optional[{new_type}] = None\n"
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        else:
            print(f"Property {property_name} not found in {file_path}. Cannot edit property.")

    print(f"Property {property_name} edited in model {entity_name} at {file_path}")
