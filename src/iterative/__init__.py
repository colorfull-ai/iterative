import subprocess
import sys
from iterative.api_processing import get_api_routers
from iterative.web import iterative_user_web_app as web_app
from iterative.cli import iterative_cli_app as cli_app

from iterative.action_processing import get_all_actions
from iterative.cli_app_integration import integrate_actions_into_cli_app
from iterative.web_app_integration import integrate_actions_into_web_app
from iterative.server_management import run_web_server, run_ngrok_subprocess
from iterative.config import Config, set_config, get_config
from iterative.cache import cache
from iterative.actions.assistant_actions import AssistantManager, ConversationManager, ask_assistant, get_assistant_info
from iterative.models.iterative import IterativeModel
from iterative.action_processing import get_all_actions
from logging import getLogger

logger = getLogger(__name__)

def prep_app():
    config = Config()
    set_config(config)
    cache.load_cache()

    actions = get_all_actions(include_project_actions=True, include_package_default_actions=True, include_api_actions=False)
    integrate_actions_into_cli_app(actions.values(), cli_app)
    integrate_actions_into_web_app(actions.values(), web_app)

    # Add routers to the web app
    logger.debug("Adding API routers to web app...")
    routers = get_api_routers()
    for router in routers:
        web_app.include_router(router)


def set_logging_level(level):
    import logging
    logging_level = get_config().get("logging_level", level)
    logging.basicConfig(level=logging_level)
    

def start_app():
    prep_app()
    cli_app()


def main():
    prep_app()
    if len(sys.argv) == 1:
        # No arguments provided, show help by running the script with '--help'
        subprocess.run(['python', __file__, '--help'])
    else:
        cli_app()

    

# Export the public API
__all__ = [
    "web_app",
    "cli_app",
    "start_util_server",
    "start_app",
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
    "get_assistant_info",
    "get_all_actions"
]

if __name__ == "__main__":
    main()