from openai import OpenAI
from iterative import get_config as _get_config
import time

class OpenAIAssistantManager:
    def __init__(self):
        self.client = OpenAI()
        self.assistant_id = _get_config.get("cli_assistant")

    def create_assistant(self, model, description=None, file_ids=None, instructions=None, metadata=None, name=None, tools=None):
        try:
            assistant = self.client.Assistants.create(
                model=model,
                description=description,
                file_ids=file_ids,
                instructions=instructions,
                metadata=metadata,
                name=name,
                tools=tools
            )
            return assistant
        except Exception as e:
            print(f"Error creating assistant: {e}")
            return None

    def run_assistant_simple_response(self, assistant_id, user_input):
        """
        Run the assistant for a simple text response.
        """
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

    def run_assistant_status_check(self, assistant_id, user_input):
        """
        Run the assistant with periodic status checks for long-running processes.
        """
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

    def run_assistant_interactive(self, assistant_id, user_input, thread_id=None):
        """
        Run the assistant for interactive conversation where multiple inputs might be sent.
        """
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

    def run_assistant_custom_logic(self, assistant_id, user_input):
        """
        Run the assistant with additional custom logic applied to the response.
        """
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

    def custom_processing(self, response):
        # Custom processing logic here
        # Replace this method with your specific logic
        return response

    def list_assistants(self):
        try:
            assistants = self.client.Assistants.list()
            return assistants.data
        except Exception as e:
            print(f"Error listing assistants: {e}")
            return None

    def update_assistant(self, assistant_id, description=None, file_ids=None, instructions=None, metadata=None, model=None, name=None, tools=None):
        try:
            updated_assistant = self.client.Assistants.update(
                assistant_id,
                description=description,
                file_ids=file_ids,
                instructions=instructions,
                metadata=metadata,
                model=model,
                name=name,
                tools=tools
            )
            return updated_assistant
        except Exception as e:
            print(f"Error updating assistant: {e}")
            return None

#  ===  Exposed AI functions  ===

def create_assistant_wrapper(model, description=None, file_ids=None, instructions=None, metadata=None, name=None, tools=None):
    manager = OpenAIAssistantManager()
    return manager.create_assistant(model, description, file_ids, instructions, metadata, name, tools)

def run_assistant_simple_response_wrapper(assistant_id, user_input):
    manager = OpenAIAssistantManager()
    return manager.run_assistant_simple_response(assistant_id, user_input)

def run_assistant_status_check_wrapper(assistant_id, user_input):
    manager = OpenAIAssistantManager()
    return manager.run_assistant_status_check(assistant_id, user_input)

def run_assistant_interactive_wrapper(assistant_id, user_input, thread_id=None):
    manager = OpenAIAssistantManager()
    return manager.run_assistant_interactive(assistant_id, user_input, thread_id)

def run_assistant_custom_logic_wrapper(assistant_id, user_input):
    manager = OpenAIAssistantManager()
    return manager.run_assistant_custom_logic(assistant_id, user_input)

def list_assistants_wrapper():
    manager = OpenAIAssistantManager()
    return manager.list_assistants()

def update_assistant_wrapper(assistant_id, description=None, file_ids=None, instructions=None, metadata=None, model=None, name=None, tools=None):
    manager = OpenAIAssistantManager()
    return manager.update_assistant(assistant_id, description, file_ids, instructions, metadata, model, name, tools)
