from openai import OpenAI
from iterative import get_config

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

# if __name__ == "__main__":
#     # # Usage
#     client = OpenAI()
#     assistant_id = "asst_puhjAkOSsC6qxJyQ7Xw9oKoq"
#     assistant_manager = AssistantManager(client)
#     conversation_manager = ConversationManager(client, assistant_id)

#     # Example calls
#     assistants = assistant_manager.list_assistants()
#     assistant_info = assistant_manager.get_assistant_info(assistant_id)
#     conversation_manager.create_conversation()
#     conversation_manager.add_message("Hello World")
#     conversation_messages = conversation_manager.process_conversation()
#     print(conversation_messages)
