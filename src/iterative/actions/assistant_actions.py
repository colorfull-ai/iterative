import json
import os
import time
from iterative.api_processing import get_api_routers as _get_api_routers
from iterative.service.assistant_manager import AssistantManager
from iterative.service.conversation_manager import ConversationManager
from iterative.service.utils.project_utils import is_cwd_iterative_project
from iterative.web_app_integration import integrate_actions_into_web_app as _integrate_actions_into_web_app
from iterative.models.assistant import IterativeAssistant
from openai import OpenAI
from iterative import get_config as _get_config
from iterative import get_all_actions as _get_all_actions
from tqdm import tqdm
from logging import getLogger as _getLogger
from termcolor import colored as _colored
import json

logger = _getLogger(__name__)


def get_assistant_info():
    client = OpenAI()
    assistant_id = _get_config().get("assistant_id")
    assistant_manager = AssistantManager(client)
    assistant_info = assistant_manager.get_assistant_info(assistant_id)

    print(_colored(f"Assistant Information: \n{json.dumps(json.loads(assistant_info), indent=2)}", 'yellow'))

    return assistant_info

def ask_assistant(message: str, assistant_id: str = None):
    client = OpenAI()
    assistant_id = _get_config().get("assistant_id")
    conversation_manager = ConversationManager(client, assistant_id)

    if not conversation_manager.current_thread:
        conversation_manager.create_conversation()

    conversation_manager.add_message(message)
    conversation_messages = conversation_manager.process_conversation()

    print(conversation_messages.data[0].content[0].text.value)

    return conversation_messages.data[0].content[0].text.value

def update_assistant_tools_with_actions():
    tools = get_actions()
    
    assistant_id = _get_config().get("assistant_id")
    client = OpenAI()
    assistant_manager = AssistantManager(client)

    # Retrieve the current assistant's properties
    current_assistant = assistant_manager.get_assistant(assistant_id)
    if current_assistant is None:
        print("Failed to retrieve current assistant.")
        return None

    # Update the tools while keeping other properties intact
    updated_assistant_properties = IterativeAssistant(
        id=current_assistant.id,
        created_at=current_assistant.created_at,
        description=current_assistant.description,
        file_ids=current_assistant.file_ids,
        instructions=current_assistant.instructions,
        metadata=current_assistant.metadata,
        model=current_assistant.model,
        name=current_assistant.name,
        object=current_assistant.object,
        tools=tools  # Update the tools
    )


    # Call the updated update_assistant method
    return assistant_manager.update_assistant(assistant_id, **updated_assistant_properties.dict())

def _get_configured_actions():
    config = _get_config()
    if not is_cwd_iterative_project():
        # only return the default actions
        actions =  _get_all_actions(include_package_default_actions=True, include_api_actions=False, include_project_actions=False)
        return actions, actions
    ai_actions = _get_all_actions(
        include_project_actions=config.get("expose_project_actions_to_ai"),
        include_package_default_actions=config.get("expose_default_actions_to_ai"),
        include_api_actions=config.get("expose_api_actions_to_ai")
    )

    cli_actions = _get_all_actions(
        include_project_actions=config.get("expose_project_actions_to_cli"),
        include_package_default_actions=config.get("expose_default_actions_to_cli"),
        # The CLI will never support API actions since the CLI can only handle Scalar arguments
        include_api_actions=False 
    )

    return ai_actions, cli_actions


def get_actions():
    from fastapi import FastAPI
    dummy_app = FastAPI()
    exposed_ai_actions, cli_actions = _get_configured_actions()

    _integrate_actions_into_web_app(exposed_ai_actions.values(), dummy_app)

    if _get_config().get("let_ai_use_apis"):
        # Add routers to the web app
        routers = _get_api_routers()
        for router in routers:
            dummy_app.include_router(router)

    openapi_schema = dummy_app.openapi()

    functions = []
    paths = openapi_schema.get('paths', {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if path == "/":
                continue
            # Create a function name based on path and method
            function_name = f"{path.replace('/', '')}"

            # Extract and format parameters
            parameters = details.get('parameters', [])
            formatted_parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            for param in parameters:
                param_name = param.get('name')
                param_type = param.get('schema', {}).get('type', 'string')
                param_description = param.get('description', '')
                formatted_parameters['properties'][param_name] = {
                    "type": param_type,
                    "description": param_description
                }
                if param.get('required', False):
                    formatted_parameters['required'].append(param_name)

            # Add function to the list
            function = {
                "type": "function",
                "function": {
                    "name": function_name,
                    "description": details.get('summary', 'No description available'),
                    "parameters": formatted_parameters
                }
            }
            functions.append(function)
            
    return functions

# def run_chat_ui():
#     """
#     Run the Streamlit chat application.
#     """
#     # Assuming your Streamlit app is in 'streamlit_app.py'
#     subprocess.run(["streamlit", "run", "streamlit_app.py"])


def interactive_session(assistant_id: str = None):
    """
    Starts an interactive session for back and forth conversation between the user and the assistant.

    Args:
        assistant_id (str, optional): The ID of the assistant. Defaults to None.

    Returns:
        None
    """
    client = OpenAI()
    if not assistant_id:
        assistant_id = _get_config().get("assistant_id")
    conversation_manager = ConversationManager(client, assistant_id)

    if not conversation_manager.current_thread:
        conversation_manager.create_conversation()

    print(_colored("Welcome to the interactive session. Type your message and press enter to get a response. Type 'quit' to end the session.", 'yellow'))
    
    while True:
        message = input(_colored("You: ", 'green'))
        if not message.strip():
            print(_colored("Message cannot be empty. Please enter a message.", 'red'))
            continue
        if message.lower() == "quit":
            print(_colored("Thank you for using the interactive session. Goodbye!", 'yellow'))
            break
        try:
            conversation_manager.add_message(message)
            conversation_messages = conversation_manager.process_conversation()
            print(_colored("Assistant: ", 'blue'), conversation_messages.data[0].content[0].text.value)
        except Exception as e:
            print(_colored(f"An error occurred: {e}", 'red'))


def execute_action_calls(json_commands):
    """
    Execute a series of function calls defined by a JSON-formatted string.
    
    The JSON string should be a serialized array of command objects. Each command object
    must contain two keys:
    
    'function': A string that specifies the name of the function to call.
                The function must exist in the global scope and be callable.
                
    'args': A dictionary where each key-value pair represents an argument name and its
            corresponding scalar value (i.e., string, integer, float, boolean, or None) to
            pass to the function. The function will be called with these arguments.
            
    All functions and arguments must be defined such that they are compatible with scalar values
    only, as complex types are not supported in this interface.
    
    Example of a valid JSON string:
    
    ```
    [
      {
        "function": "update_project_config_value",
        "args": {"key": "database_port", "value": 5432}
      },
      {
        "function": "enable_feature",
        "args": {"feature_name": "logging", "status": true}
      },
      // Add more function calls as needed
    ]
    ```
    
    Args:
        json_commands (str): A JSON string representing an ordered list of function calls
                             and their scalar arguments. The commands will be executed in
                             the order they appear in the string.
                             
    Raises:
        json.JSONDecodeError: If `json_commands` is not a valid JSON string.
        Exception: For any issues during function execution, including if a function is not
                   found, or if there is a mismatch between provided arguments and the
                   function's parameters.
    """
    try:
        actions = _get_all_actions()
        # Deserialize the JSON string into a Python object
        commands = json.loads(json_commands)
        
        # Iterate over the list of commands
        for command in commands:
            function_name = command['function']
            args = command['args']

            actions_to_call = actions.get(function_name)
            print(actions_to_call)

            if callable(actions_to_call.function):
                # Execute the function with the provided arguments
                actions_to_call.function(**args)
            else:
                logger.error(f"Function {function_name} not found or is not callable.")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except Exception as e:
        logger.error(f"Error executing function calls: {e}")


def set_docs_as_knowledge():
    """
    Searches for a specified folder and uploads its contents to OpenAI.

    Args:
        folder_path (str): The path to the folder whose contents are to be uploaded.

    Returns:
        list: A list of uploaded file references, or None if an error occurs.
    """
    folder_path = _get_config().get("docs_path", "docs")

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logger.error(f"Folder '{folder_path}' does not exist or is not a directory.")
        return None

    try:
        client = OpenAI()  # Initialize the OpenAI client
        assistant_manager = AssistantManager(client)  # Initialize the AssistantManager

        files = assistant_manager.upload_docs_folder(folder_path)

        ids = [file.id for file in files]
        print(f"File IDs: {ids}")

        # Update the assistant's file IDs
        assistant_id = _get_config().get("assistant_id")
        print(f"assistant_id: {assistant_id}")

        assistant_manager.update_assistant(assistant_id, file_ids=ids)
        return "updated the assistant with knowledge in the docs folder"
    except Exception as e:
        logger.error(f"Error occurred during document upload: {e}")
        return None


def delete_files():
    """
    Searches for a specified folder and uploads its contents to OpenAI.

    Args:
        folder_path (str): The path to the folder whose contents are to be uploaded.

    Returns:
        list: A list of uploaded file references, or None if an error occurs.
    """
    client = OpenAI()  # Initialize the OpenAI client
    assistant_manager = AssistantManager(client)  # Initialize the AssistantManager

    files = assistant_manager.retrieve_files()

    for file in files:
        assistant_manager.delete_file(file.id)