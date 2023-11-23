import os
from textwrap import dedent
from typing import Dict, List, Optional
from iterative.config import _get_global_config

def create_model(entity_name: str, model_generation_path: Optional[str] = None):
    """
    Create a basic nosql_yorm model file with the given entity name in a 'models' directory.

    Args:
        entity_name (str): Name of the entity for which the model is to be created.
        model_generation_path (Optional[str]): Path where the model file will be created. Defaults to the current working directory.
    """
    # Fetch the model generation path from the global configuration if not provided
    if not model_generation_path:
        config = _get_global_config()
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
        file.write(dedent(model_content))

    print(f"Model {class_name} created at {file_path}")


def add_property_to_model(entity_name: str, property_name: str, property_type: str, model_generation_path: str = None):
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
