import os
import typer
from .util_server import discover_scripts, run_web_server, cli_app, web_app
from .config import Config, set_global_config, _get_global_config
import logging
from . import logging as package_logging

app = typer.Typer()

@app.command()
def start_util_server(
    port: int = typer.Option(5279, help="Port number for the utility server"),
    config_path: str = typer.Option(None, help="Path to the configuration file")
):
    """
    Starts the utility server on the specified port.
    """
    load_configuration(config_path)
    run_web_server(port)

def load_configuration(custom_config_path: str = None):
    # Default config file next to admin.py
    default_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

    # Use the custom config path if provided, otherwise use the default
    final_config_path = custom_config_path if custom_config_path else default_config_path

    # Load and set the configuration
    config = Config(final_config_path)
    set_global_config(config)

    # Log the usage of default configuration if custom config is not provided
    if not custom_config_path:
        logger = logging.getLogger("admin")
        logger.info("Using default configuration.")


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
    "set_global_config",
    "_get_global_config"
    "logging",
    "package_logging"  # Only if you have custom logging functionality in your package
]