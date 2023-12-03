# src/iterative/cli.py

import sys
from iterative.server_management import run_web_server
import typer
import os

iterative_cli_app = typer.Typer()

def find_iterative_root(starting_directory):
    current_directory = starting_directory
    root_directory = os.path.abspath(os.sep)

    while current_directory != root_directory:
        # List only directories starting with '.'
        directories = [d for d in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, d)) and d.startswith('.')]
        
        if '.iterative' in directories:
            return current_directory

        current_directory = os.path.dirname(current_directory)

    return None  # Return None if .iterative directory is not found


@iterative_cli_app.command()
def start_server(
    port: int = typer.Option(5279, help="Port number for the utility server"),
    config_path: str = typer.Option(None, help="Path to the configuration file")
):
    """
    Starts the utility server on the specified port.
    """
    run_web_server(port)

