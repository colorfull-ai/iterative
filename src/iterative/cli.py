# src/iterative/cli.py

from iterative.server_management import run_web_server
import typer

iterative_cli_app = typer.Typer()


@iterative_cli_app.command()
def start_server():
    """
    Starts the utility server on the specified port.
    """
    run_web_server()

