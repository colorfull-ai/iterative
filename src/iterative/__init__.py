from iterative.commands.template_commands import init
import typer
from iterative.util_server import discover_actions, run_web_server, run_ngrok_subprocess
from iterative.user_cli import cli_app
from iterative.web import web_app as app
from iterative.config import Config, set_config, get_config
from iterative.models import IterativeModel
from iterative.cache import cache
from iterative.scripts.ai_functions import AssistantManager, ConversationManager

@cli_app.command()
def start_util_server(
    port: int = typer.Option(5279, help="Port number for the utility server"),
    config_path: str = typer.Option(None, help="Path to the configuration file")
):
    """
    Starts the utility server on the specified port.
    """
    run_web_server(port)

@cli_app.command()
def init_command(directory: str):
    """
    Initialize a new iterative app in the specified directory.
    """
    init(directory)

def prep_app():
    config = Config(user_config_path="config.yaml")
    set_config(config)
    cache.load_cache()
    discover_actions(cli_app, app)

def start_app():
    prep_app()
    cli_app()

prep_app()


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
    "ConversationManager"
]