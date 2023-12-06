import json
import time
from typing import Dict, List
from iterative.api_processing import get_api_routers as _get_api_routers
from iterative.web_app_integration import integrate_actions_into_web_app as _integrate_actions_into_web_app
from openai import OpenAI
from iterative import get_config as _get_config
from iterative import get_all_actions as _get_all_actions
from tqdm import tqdm
from logging import getLogger as _getLogger
from termcolor import colored as _colored
import json

logger = _getLogger(__name__)


class AssistantManager:
    def __init__(self, client):
        self.client: OpenAI = client

    def list_assistants(self):
        try:
            assistants = self.client.beta.assistants.list()
            return assistants.data
        except Exception as e:
            print(f"Error listing assistants: {e}")
            return None

    def get_assistant(self, asst_id=None):
        try:
            if not asst_id:
                asst_id = _get_config().get("assistant_id")

            assistant = self.client.beta.assistants.retrieve(asst_id)
            return assistant
        except Exception as e:
            print(f"Error getting assistant: {e}")
            return None

    def get_assistant_info(self, asst_id=None):
        try:
            if not asst_id:
                asst_id = _get_config().get("assistant_id")
            assistant = self.client.beta.assistants.retrieve(asst_id)
            return assistant.json()
        except Exception as e:
            print(f"Error getting assistant: {e}")
            return None
        
    def update_assistant(self, asst_id=None, **kwargs):
        try:
            if not asst_id:
                asst_id = _get_config().get("assistant_id")
            
            if not asst_id:
                print("No assistant ID provided.")
                return 
            
            assistant = self.client.beta.assistants.update(asst_id, **kwargs)
            return assistant
        except Exception as e:
            print(json.dumps(e, indent=2))
            # print(f"Error updating assistant: {e}")
            return None

class ConversationManager:
    def __init__(self, client, assistant_id):
        self.client: OpenAI = client
        self.assistant_id = assistant_id
        self.current_thread = _get_config().get("assistant_conversation_thread_id")
        self.current_run = None
        self.actions = _get_all_actions()

    def create_conversation(self):
        self.current_thread = self.client.beta.threads.create()
        return self.current_thread

    def add_message(self, message: str):
        if not self.current_thread:
            raise Exception("No active conversation thread.")
        return self.client.beta.threads.messages.create(
            thread_id=self.current_thread.id,
            content=message,
            role="user"
        )

    def process_conversation(self):
        logger.debug("Processing conversation...")

        if not self.current_thread:
            raise Exception("No active conversation thread.")

        self.current_run = self.client.beta.threads.runs.create(
            thread_id=self.current_thread.id,
            assistant_id=self.assistant_id
        )

        # Continuously check the status of the conversation
        while True:
            self.current_run = self.client.beta.threads.runs.retrieve(
                thread_id=self.current_thread.id,
                run_id=self.current_run.id
            )

            if self.current_run.status == "requires_action":
                self.handle_required_action()
            elif self.current_run.status in ["cancelled", "cancelling", "completed", "failed", "expired"]:
                break

            time.sleep(1)  # Avoid too frequent polling

        messages = self.client.beta.threads.messages.list(
            thread_id=self.current_thread.id
        )
        return messages

    def handle_required_action(self):
        # Assuming the tool call details are in current_run.required_action
        required_action = self.current_run.required_action
        outputs = required_action.submit_tool_outputs
        actual_action_outputs = []
        for tool_call in outputs.tool_calls:
            tool_call_id = tool_call.id
            
            function_name, args = tool_call.function.name, tool_call.function.arguments
            # Execute the action
            action_output = self.execute_action(function_name, **json.loads(args))
            actual_action_outputs.append({"tool_call_id": tool_call_id, "output": json.dumps(action_output)})


        # Submit the tool output back to OpenAI
        self.submit_tool_outputs(actual_action_outputs)


    def execute_action(self, action_name: str, **kwargs):
        action = self.actions.get(action_name)
        if not action:
            raise Exception(f"Action {action_name} not found.")
        action_result = action.get_function()(**kwargs)
        return action_result

    def submit_tool_outputs(self, tool_outputs: List[Dict]):
        logger.debug("Submitting tool outputs...")

        for _ in tqdm(range(300), desc="Submitting...", leave=False):
            time.sleep(0.03)

        run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.current_thread.id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs
        )
        return run

def get_assistant_info():
    client = OpenAI()
    assistant_id = _get_config().get("assistant_id")
    assistant_manager = AssistantManager(client)
    assistant_info = assistant_manager.get_assistant_info(assistant_id)
    assistant = assistant_manager.get_assistant(assistant_id)

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

    return assistant_manager.update_assistant(assistant_id, tools=tools)

def get_actions():
    from fastapi import FastAPI
    dummy_app = FastAPI()
    actions = _get_all_actions(include_project_actions=True, include_package_default_actions=True, include_api_actions=False)
    _integrate_actions_into_web_app(actions.values(), dummy_app)

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