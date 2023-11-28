from typing import Any, Optional, Tuple
from openai import OpenAI
from iterative.config import get_config as _get_config
import time

class OpenAIAssistantManager:
    def __init__(self) -> None:
        self.client: OpenAI = OpenAI()
        self.assistant_id: str = _get_config().get("cli_assistant")

    def create_assistant(self, model: str, description: Optional[str] = None, 
                         instructions: Optional[str] = None, name: Optional[str] = None) -> Any:
        try:
            assistant = self.client.beta.assistants.create(
                model=model,
                description=description,
                instructions=instructions,
                name=name
            )
            return assistant
        except Exception as e:
            print(f"Error creating assistant: {e}")
            return None

    def run_assistant_simple_response(self, assistant_id: str, user_input: str) -> Optional[str]:
        try:
            thread = self.client.beta.threads.create(assistant_id=assistant_id)
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content={'text': {'value': user_input}}
            )
            response = self.client.beta.threads.messages.list(thread_id=thread.id).data[-1].content['text']['value']
            return response
        except Exception as e:
            print(f"Error running assistant: {e}")
            return None

    def run_assistant_status_check(self, assistant_id: str, user_input: str) -> Optional[str]:
        try:
            thread = self.client.beta.threads.create(assistant_id=assistant_id)
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content={'text': {'value': user_input}}
            )
            time.sleep(2)
            while True:
                messages = self.client.beta.threads.messages.list(thread_id=thread.id).data
                if messages and messages[-1].role == "assistant":
                    return messages[-1].content['text']['value']
                time.sleep(1)
        except Exception as e:
            print(f"Error running assistant: {e}")
            return None

    def run_assistant_interactive(self, assistant_id: str, user_input: str, thread_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        try:
            if not thread_id:
                thread = self.client.beta.threads.create(assistant_id=assistant_id)
                thread_id = thread.id

            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content={'text': {'value': user_input}}
            )

            response = self.client.beta.threads.messages.list(thread_id=thread_id).data[-1].content['text']['value']
            return response, thread_id
        except Exception as e:
            print(f"Error running assistant: {e}")
            return None, None

    def run_assistant_custom_logic(self, assistant_id: str, user_input: str) -> Optional[Any]:
        try:
            thread = self.client.beta.threads.create(assistant_id=assistant_id)
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content={'text': {'value': user_input}}
            )

            response = self.client.beta.threads.messages.list(thread_id=thread.id).data[-1].content['text']['value']
            processed_response = self.custom_processing(response)
            return processed_response
        except Exception as e:
            print(f"Error running assistant: {e}")
            return None

    def custom_processing(self, response: str) -> str:
        return response

    def list_assistants(self) -> Optional[Any]:
        try:
            assistants = self.client.beta.assistants.list()
            return assistants.data
        except Exception as e:
            print(f"Error listing assistants: {e}")
            return None

    def update_assistant(self, assistant_id: str, update_field: str, new_value: str) -> Any:
        try:
            update_params = {update_field: new_value}
            updated_assistant = self.client.beta.assistants.update(
                assistant_id,
                **update_params
            )
            return updated_assistant
        except Exception as e:
            print(f"Error updating assistant: {e}")
            return None

    def list_available_models(self) -> Any:
        try:
            return self.client.models.list()
        except Exception as e:
            print(f"Error listing models: {e}")
            return None
        
    def get_last_message(self, thread_id):
        try:
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            if messages.data:
                return messages.data[-1].content['text']['value']
            else:
                return "No response received."
        except Exception as e:
            print(f"Error getting last message: {e}")
            return None

#  ===  Exposed AI functions  ===

def create_assistant_wrapper(model: str, description: Optional[str] = None, 
                             instructions: Optional[str] = None, 
                             name: Optional[str] = None) -> Any:
    manager = OpenAIAssistantManager()
    return manager.create_assistant(model, description, instructions, name)

def update_assistant_wrapper(assistant_id: str, update_field: str, new_value: str) -> Any:
    manager = OpenAIAssistantManager()
    return manager.update_assistant(assistant_id, update_field, new_value)

def run_assistant_simple_response_wrapper(assistant_id: str, user_input: str) -> Optional[str]:
    manager = OpenAIAssistantManager()
    return manager.run_assistant_simple_response(assistant_id, user_input)

def run_assistant_status_check_wrapper(assistant_id: str, user_input: str) -> Optional[str]:
    manager = OpenAIAssistantManager()
    return manager.run_assistant_status_check(assistant_id, user_input)

def run_assistant_interactive_wrapper(assistant_id: str, user_input: str, thread_id: Optional[str] = None):
    manager = OpenAIAssistantManager()
    return manager.run_assistant_interactive(assistant_id, user_input, thread_id)

def run_assistant_custom_logic_wrapper(assistant_id: str, user_input: str) -> Optional[Any]:
    manager = OpenAIAssistantManager()
    return manager.run_assistant_custom_logic(assistant_id, user_input)

def list_assistants_wrapper() -> Optional[Any]:
    manager = OpenAIAssistantManager()
    return manager.list_assistants()

def list_available_models_wrapper() -> Any:
    manager = OpenAIAssistantManager()
    return manager.list_available_models()
