from iterative.commands.template_commands import init
import typer
from iterative.util_server import discover_scripts, run_web_server
from iterative.user_cli import cli_app
from iterative.web import web_app as app
from iterative.config import Config, set_config
from iterative.models import IterativeModel
from iterative.cache import cache

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


def start_app():
    cache.load_cache()
    discover_scripts(cli_app, app)
    cli_app()

discover_scripts(cli_app, app)


# Export the public API
__all__ = [
    "app",
    "start_util_server",
    "start_app",
    "discover_scripts",
    "run_web_server",
    "Config",
    "set_config",
    "_get_global_config"
    "logging",
    "package_logging",  # Only if you have custom logging functionality in your package
    "cache",
    "IterativeModel"
]