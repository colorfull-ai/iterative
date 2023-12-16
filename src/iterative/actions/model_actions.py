import os
from textwrap import dedent as _dedent
from typing import  Optional
import humps
from iterative.config import get_config as _get_config
from iterative.service.utils.project_utils import create_project_path as _create_project_path
from pydantic2ts import generate_typescript_defs

def generate_model(entity_name: str, model_generation_path: Optional[str] = None):
    """
    Create a basic nosql_yorm model file with the given entity name in a 'models' directory.
    Also updates __init__.py to import the new model and add it to the __all__ list.
    """
    # Fetch the model generation path from the global configuration if not provided
    if not model_generation_path:
        model_generation_path = _get_config().get('model_generation_path')

    # Append 'models' to the model generation path to ensure the directory structure
    model_folder = _create_project_path(model_generation_path)

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
    return model_content



def add_property_to_model(entity_name: str, property_name: str, property_type: str, model_generation_path: Optional[str] = None):
    """
    Add a new property to an existing nosql_yorm model. using Python property types that you could find in the typing module.

    Args:
        entity_name: Name of the entity to which the property should be added.
        property_type: The python data type of the property a primitive or Typing type.
    """
    model_folder = _create_project_path(model_generation_path)
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
    return new_property_line

def edit_property_in_model(entity_name: str, property_name: str, new_type: str, model_generation_path: Optional[str] = None):
    """
    Edit an existing property in a nosql_yorm model.

    Args:
        entity_name: Name of the entity to which the property belongs.
        new_type: The new python data type of the property a primitive or Typing type.
    """
    model_folder = _create_project_path(model_generation_path)
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
    return lines[property_line_index]


def generate_ts_client_for_model(model_name: str):
    """
    Generates a TypeScript client class for interacting with CRUD endpoints of a given model.
    """
    model_name_camel = humps.camelize(model_name)  # CamelCase
    model_name_pascal = humps.pascalize(model_name)  # CamelCase
    model_name_snake = humps.decamelize(model_name)  # snake_case
    model_name_plural_snake = humps.decamelize(model_name) + 's'  # snake_case plural
    model_name_plural_camel = humps.camelize(model_name) + 's'  # CamelCase plural

    ts_client = _dedent(f"""
    import {{ {model_name_pascal} }} from '../models/{model_name_snake}Models';
    import {{ BaseClient }} from './baseClient';

    export class {model_name_camel}Client extends BaseClient {{
        
        public static async get{model_name_plural_camel}(page: number = 1, pageSize: number = 10): Promise<{model_name_pascal}[]> {{
            const endpoint = `/{model_name_plural_snake}?page=${{page}}&page_size=${{pageSize}}`;
            return this.fetchData(endpoint);
        }}

        public static async get{model_name_camel}(id: string): Promise<{model_name_pascal}> {{
            const endpoint = `/{model_name_plural_snake}/${{id}}`;
            return this.fetchData(endpoint);
        }}

        public static async create{model_name_camel}({model_name_snake}: {model_name_pascal}): Promise<{model_name_pascal}> {{
            const endpoint = `/{model_name_plural_snake}`;
            return this.postData(endpoint, {model_name_snake});
        }}

        public static async update{model_name_camel}(id: string, {model_name_snake}: {model_name_pascal}): Promise<{model_name_pascal}> {{
            const endpoint = `/{model_name_plural_snake}/${{id}}`;
            return this.putData(endpoint, {model_name_snake});
        }}

        public static async delete{model_name_camel}(id: string): Promise<void> {{
            const endpoint = `/{model_name_plural_snake}/${{id}}`;
            return this.deleteData(endpoint);
        }}
    }}
    """)
    clients_folder = _create_project_path(_get_config().get("ui_path"), _get_config().get("ui_clients_path"))
    
    # Ensure the output directory exists
    os.makedirs(clients_folder, exist_ok=True)

    # Write the TypeScript client to a file
    ts_client_file_path = os.path.join(clients_folder, f"{model_name_snake}Client.ts")
    with open(ts_client_file_path, 'w') as file:
        file.write(ts_client)

    print(f"TypeScript client for {model_name} created at {ts_client_file_path}")
    return ts_client




