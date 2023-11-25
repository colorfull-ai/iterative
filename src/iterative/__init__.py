import os
from iterative.commands.template_commands import init
import typer
from iterative.util_server import discover_scripts, run_web_server, cli_app, web_app
from iterative.config import Config, set_config, get_config
import logging
from nosql_yorm.cache import cache_handler as cache
from iterative.models import IterativeModel


app = typer.Typer()

@app.command()
def start_util_server(
    port: int = typer.Option(5279, help="Port number for the utility server"),
    config_path: str = typer.Option(None, help="Path to the configuration file")
):
    """
    Starts the utility server on the specified port.
    """
    run_web_server(port)

@app.command()
def init_command(directory: str):
    """
    Initialize a new iterative app in the specified directory.
    """
    init(directory)


def start_app():
    app.add_typer(cli_app, name="scripts")
    discover_scripts(cli_app, web_app)
    app()



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