import inspect
from typing import Any, Dict, List
from openai import OpenAI
from iterative import get_config
from openai_assistant_toolkit import create_function_tool_from_callback

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
                asst_id = get_config().get("assistant_id")

            assistant = self.client.beta.assistants.retrieve(asst_id)
            return assistant.data
        except Exception as e:
            print(f"Error getting assistant: {e}")
            return None

    def get_assistant_info(self, asst_id=None):
        try:
            if not asst_id:
                asst_id = get_config().get("assistant_id")
            assistant = self.client.beta.assistants.retrieve(asst_id)
            return assistant.json()
        except Exception as e:
            print(f"Error getting assistant: {e}")
            return None

class ConversationManager:
    def __init__(self, client, assistant_id):
        self.client: OpenAI = client
        self.assistant_id = assistant_id
        self.current_thread = get_config().get("assistant_conversation_thread_id")
        self.current_run = None

    def create_conversation(self):
        if not self.current_thread:
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
        if not self.current_thread:
            raise Exception("No active conversation thread.")
        self.current_run = self.client.beta.threads.runs.create(
            thread_id=self.current_thread.id,
            assistant_id=self.assistant_id
        )

        while self.current_run.status not in ["cancelled", "cancelling", "completed", "failed", "expired"]:
            self.current_run = self.client.beta.threads.runs.retrieve(
                thread_id=self.current_thread.id,
                run_id=self.current_run.id
            )
        messages = self.client.beta.threads.messages.list(
            thread_id=self.current_thread.id
        )
        return messages


def get_assistant_info():
    client = OpenAI()
    assistant_id = get_config().get("assistant_id")
    assistant_manager = AssistantManager(client)
    return assistant_manager.get_assistant_info(assistant_id)

def ask_assistant(message: str, assistant_id: str = None, verbose: bool = False):
    client = OpenAI()
    assistant_id = get_config().get("assistant_id")
    conversation_manager = ConversationManager(client, assistant_id)

    conversation_manager.create_conversation()
    conversation_manager.add_message(message)
    conversation_messages = conversation_manager.process_conversation()
    if verbose:
        print(conversation_messages.data)
    return conversation_messages.data[0].content[0].text.value

def give_assistant_tools(cli_app, web_app):
    cli_functions = parse_typer_app(cli_app)
    web_functions = parse_fastapi_app(web_app)

    tools = []
    tools.extend(cli_functions)
    tools.extend(web_functions)
    return tools

def parse_typer_app(app) -> List[Dict[str, Any]]:
    # Extract commands from the Typer app
    functions = []
    for command_info in app.registered_commands:
        # Typer stores the command name in the 'name' attribute of the CommandInfo object
        command_name = command_info.name
        command_callback = command_info.callback
        function = create_function_tool_from_callback(command_name, command_callback)
        functions.append(function)
    return functions


def parse_fastapi_app(app) -> List[Dict[str, Any]]:
    # Extract routes from the FastAPI app
    functions = []
    for route in app.routes:
        # Assuming each route is a standard FastAPI route with relevant attributes
        if hasattr(route, "methods") and hasattr(route, "endpoint"):
            function = create_function_tool_from_endpoint(route)
            functions.append(function)
    return functions

def create_function_tool_from_callable(name, callback):
    create_function_tool_from_callback(name, callback)

def create_function_tool_from_endpoint(route):
    # Generate function tool from a FastAPI route
    method = route.methods
    path = route.path
    callback = route.endpoint
    description = callback.__doc__ or ""
    name = callback.__name__

    # Extracting parameter details from the callback function
    params = inspect.signature(callback).parameters
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in params.items():
        parameters["properties"][param_name] = {
            "type": str(param.annotation),
            "description": param_name  # or a more detailed description if available
        }
        if param.default is param.empty:
            parameters["required"].append(param_name)

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    }