from iterative.action_processing import get_all_actions
from iterative.cli_app_integration import integrate_actions_into_cli_app
from iterative.web_app_integration import integrate_actions_into_web_app
from iterative.server_management import run_web_server
from iterative.user_cli import iterative_cli_app as iterative_user_cli_app
from iterative.web import web_app as iterative_user_web_app
from iterative.cli import app as iterative_package_cli_app
from iterative.config import Config, set_config, get_config
from iterative.models import IterativeModel
from iterative.cache import cache
from iterative.actions.ai_actions import AssistantManager, ConversationManager, ask_assistant, get_assistant_info


def prep_app():
    config = Config(user_config_path="config.yaml")
    set_config(config)
    cache.load_cache()
    actions = get_all_actions()
    print(f"Found {len(actions)} actions.")
    integrate_actions_into_cli_app(actions, iterative_package_cli_app)
    integrate_actions_into_cli_app(actions, iterative_user_cli_app)
    integrate_actions_into_web_app(actions, iterative_user_web_app)
    

def start_app():
    prep_app()
    iterative_user_cli_app()

def main():
    prep_app()
    iterative_package_cli_app()


# Export the public API
__all__ = [
    "app",
    "start_util_server",
    "start_app",
    "discover_actions",
    "run_web_server",
    "Config",
    "set_config",
    "logging",
    "package_logging",  # Only if you have custom logging functionality in your package
    "cache",
    "IterativeModel",
    "run_ngrok_subprocess",
    "get_config",
    "AssistantManager",
    "ConversationManager",
    "ask_assistant",
    "get_assistant_info"
]