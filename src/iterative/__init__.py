import subprocess
import sys

from nosql_yorm import NameSpacedCache
from nosql_yorm.models import set_firestore_client
from iterative.service.utils.project_utils import get_project_root
from iterative.service.utils.api_utils import find_api_routers_in_parent_project
from iterative.web import iterative_user_web_app as web_app
from iterative.cli import iterative_cli_app as cli_app

from iterative.service.utils.action_utils import get_all_actions
from iterative.cli_app_integration import integrate_actions_into_cli_app
from iterative.web_app_integration import add_routers_to_web_app, integrate_actions_into_web_app
from iterative.server_management import run_web_server, run_ngrok_subprocess
from iterative.config import Config, set_config, get_config
from iterative.cache import cache
from iterative.actions.assistant_actions import AssistantManager, ConversationManager, _get_configured_actions, ask_assistant, get_assistant_info
from iterative.models.iterative import IterativeModel
from iterative.models.config import IterativeAppConfig
from iterative.service.utils.action_utils import get_all_actions
from iterative.actions.assistant_actions import update_assistant_tools_with_actions
from logging import getLogger
import logging

logger = getLogger(__name__)

def prep_app():
    config = Config()
    set_config(config)
    cache.load_cache()

    LOGGING_LEVELS = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }

    logging_level = get_config().get("logging_level", "INFO")
    logging_level = LOGGING_LEVELS.get(logging_level.upper(), logging.INFO)
    logging.basicConfig(level=logging_level)

    web_actions, cli_actions = _get_configured_actions()
    integrate_actions_into_web_app(web_actions.values(), web_app)
    integrate_actions_into_cli_app(cli_actions.values(), cli_app)

    logger.info(f"Adding routers to web app")
    add_routers_to_web_app(web_app)

    update_assistant_tools_with_actions()


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
    "prep_app",
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
    "get_all_actions",
    "NameSpacedCache",
    "set_firestore_client",
    "get_project_root",
    "IterativeAppConfig",
]

if __name__ == "__main__":
    main()