import typer
from iterative.server_management import run_web_server
from iterative.commands.template_commands import init


iterative_cli_app = typer.Typer()


@iterative_cli_app.command()
def start_util_server(
    port: int = typer.Option(5279, help="Port number for the utility server"),
    config_path: str = typer.Option(None, help="Path to the configuration file")
):
    """
    Starts the utility server on the specified port.
    """
    run_web_server(port)

@iterative_cli_app.command()
def init_command(directory: str):
    """
    Initialize a new iterative app in the specified directory.
    """
    init(directory)