# src/iterative/cli.py

import sys
from iterative.server_management import run_web_server
import typer
import os

iterative_cli_app = typer.Typer()


@iterative_cli_app.command()
def start_server():
    """
    Starts the utility server on the specified port.
    """
    run_web_server()

