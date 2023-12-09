import os
from textwrap import dedent as _dedent
from typing import  Optional
import humps
from iterative.config import get_config as _get_config
# from pydantic2ts import generate_typescript_defs

def generate_model(entity_name: str, model_generation_path: Optional[str] = None):
    """
    Create a basic nosql_yorm model file with the given entity name in a 'models' directory.
    Also updates __init__.py to import the new model and add it to the __all__ list.
    """
    # Fetch the model generation path from the global configuration if not provided
    if not model_generation_path:
        model_generation_path = _get_config().get('model_generation_path')

    # Append 'models' to the model generation path to ensure the directory structure
    model_folder = os.path.join(os.getcwd(), model_generation_path)

    # Create the models directory if it doesn't exist
    try:
        os.makedirs(model_folder, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {model_folder}: {e}")
        return

    # Generate file name in snake case and class name in pascal case
    file_name = humps.decamelize(entity_name) + ".py"
    class_name = humps.pascalize(entity_name)

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


# def generate_ts_definitions_from_pydantic(module_path: str, output_file_path: str):
#     """
#     Generates TypeScript definitions from a Pydantic module and saves them to a file.

#     Args:
#         module_path (str): The import path of the Pydantic module (e.g., 'backend.api').
#         output_file_path (str): The path to the output TypeScript file.
#     """
#     try:
#         # Generate TypeScript definitions
#         ts_definitions = generate_typescript_defs(module_path)

#         # Save the definitions to the specified output file
#         with open(output_file_path, 'w') as file:
#             file.write(ts_definitions)
        
#         print(f"TypeScript definitions generated and saved to {output_file_path}")
#     except Exception as e:
#         print(f"An error occurred while generating TypeScript definitions: {e}")
