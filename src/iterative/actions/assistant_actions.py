import json
import time
from iterative.api_processing import get_api_routers as _get_api_routers
from iterative.service.assistant_manager import AssistantManager
from iterative.service.conversation_manager import ConversationManager
from iterative.web_app_integration import integrate_actions_into_web_app as _integrate_actions_into_web_app
from iterative.models.assistant import IterativeAssistant
from openai import OpenAI
from typing import Dict, List
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
    logger.debug("Assistant Information:", assistant_info)

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

    # check if cli_actions is in ai_actions and if not add them and integrate with web app, filter first
    actions = {}
    for action in cli_actions.values():
        if action.id not in exposed_ai_actions:
            exposed_ai_actions[action.id] = action
            actions[action.id] = action
        
    
    _integrate_actions_into_web_app(actions.values(), dummy_app)

    if _get_config().get("let_ai_use_apis"):
        # Add routers to the web app
        logger.debug("Adding API routers to web app...")
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
        # Deserialize the JSON string into a Python object
        commands = json.loads(json_commands)
        
        # Iterate over the list of commands
        for command in commands:
            function_name = command['function']
            args = command['args']

            # Ensure the function exists and is callable
            function_to_call = globals().get(function_name)
            if callable(function_to_call):
                # Execute the function with the provided arguments
                function_to_call(**args)
            else:
                logger.error(f"Function {function_name} not found or is not callable.")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except Exception as e:
        logger.error(f"Error executing function calls: {e}")