import os
import re
from textwrap import dedent as _dedent
from typing import  Optional
from iterative.config import get_config as _get_config
from iterative.actions.api_actions import _generate_crud_endpoints
import humps

def generate_endpoints_for_model(model_name: str, models_path: Optional[str] = None, endpoints_path: Optional[str] = None):
    """
    Generate FastAPI CRUD endpoints for a given model and save them in the 'endpoints' directory.

    """
    # Fetch paths from the global configuration if not provided
    if not models_path or not endpoints_path:
        base_path = _get_config().config.get('model_generation_path', os.getcwd())
        models_path = models_path or os.path.join(base_path, 'models')
        endpoints_path = endpoints_path or os.path.join(base_path, 'endpoints')

    # Ensure the 'models' directory exists
    if not os.path.exists(models_path):
        print(f"Models directory {models_path} does not exist.")
        return
    
    # Ensure the 'endpoints' directory exists
    os.makedirs(endpoints_path, exist_ok=True)

    model_file_name = f"{model_name}.py"
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


def generate_model(entity_name: str, model_generation_path: Optional[str] = None):
    """
    Create a basic nosql_yorm model file with the given entity name in a 'models' directory.
    Also updates __init__.py to import the new model and add it to the __all__ list.
    """
    # Fetch the model generation path from the global configuration if not provided
    if not model_generation_path:
        model_generation_path = _get_config().get('model_generation_path', os.getcwd())

    # Append 'models' to the model generation path to ensure the directory structure
    model_folder = os.path.join(model_generation_path, 'models')

    # Create the models directory if it doesn't exist
    try:
        os.makedirs(model_folder, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {model_folder}: {e}")
        return

    # Generate the model class content
    class_name = entity_name.title().replace('_', '')
    file_name = f"{class_name}.py"
    file_path = os.path.join(model_folder, file_name)
    model_content = _dedent(f"""\
    from iterative import IterativeModel
    from typing import *
    from iterative.models import * 
                            

    class {class_name}(IterativeModel):
        _collection_name = "{class_name}"
        # TODO: Add fields here
    """)

    # Write the model class to the file
    with open(file_path, 'w') as file:
        file.write(model_content)

    # Update __init__.py to import the new model and add it to __all__
    init_file = os.path.join(model_folder, '__init__.py')
    init_content = ""
    if os.path.exists(init_file):
        with open(init_file, 'r') as file:
            init_content = file.read()

    # Append import statement
    init_content += f"from .{class_name} import {class_name}\n"

    # Update __all__ list
    all_match = re.search(r'__all__\s*=\s*\[([^\]]*)\]', init_content)
    if all_match:
        all_list = all_match.group(1) + f', "{class_name}"'
        init_content = re.sub(r'__all__\s*=\s*\[([^\]]*)\]', f'__all__ = [{all_list}]', init_content)
    else:
        init_content += f'\n__all__ = ["{class_name}"]\n'

    with open(init_file, 'w') as file:
        file.write(init_content)

    print(f"Model {class_name} created at {file_path}")


def add_property_to_model(entity_name: str, property_name: str, property_type: str, model_generation_path: Optional[str] = None):
    """
    Add a new property to an existing nosql_yorm model.

    Args:
        entity_name: Name of the entity to which the property should be added.
        property_type: The python data type of the property a primitive or Typing type.
    """
    model_folder = model_generation_path or os.getcwd()
    file_name = f"{entity_name}.py"
    file_path = os.path.join(model_folder, "models", file_name)

    if not os.path.exists(file_path):
        print(f"Model file {file_path} does not exist.")
        raise FileNotFoundError(f"Model file {file_path} does not exist.")

    new_property_line = f"    {property_name}: Optional[{property_type}] = None\n"

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        insert_line_index = next((i for i, line in enumerate(lines) if '_collection_name' in line), None)

        if insert_line_index is not None:
            lines.insert(insert_line_index + 1, new_property_line)
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        else:
            print(f"Collection name not found in {file_path}. Cannot add property.")

    print(f"Property {property_name} added to model {entity_name} at {file_path}")

def edit_property_in_model(entity_name: str, property_name: str, new_type: str, model_generation_path: Optional[str] = None):
    """
    Edit an existing property in a nosql_yorm model.

    Args:
        entity_name: Name of the entity to which the property belongs.
        new_type: The new python data type of the property a primitive or Typing type.
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
            lines[property_line_index] = f"    {property_name}: Optional[{new_type}] = None\n"
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        else:
            print(f"Property {property_name} not found in {file_path}. Cannot edit property.")

    print(f"Property {property_name} edited in model {entity_name} at {file_path}")

