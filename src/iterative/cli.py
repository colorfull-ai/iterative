import os
import subprocess
from iterative.server_management import run_web_server
import typer
from iterative.service.utils import doc_utils
from iterative.service.utils.project_utils import get_project_root

iterative_cli_app = typer.Typer()

@iterative_cli_app.command()
def start_server():
    run_web_server()


@iterative_cli_app.command()
def run_streamlits():
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the path to the streamlit_app.py file
    streamlit_app_path = os.path.join(current_dir, "ui", "streamlit_app.py")

    subprocess.run(["streamlit", "run", streamlit_app_path])


@iterative_cli_app.command()
def serve_docs(port: str = typer.Option("4500", help="The port to serve the docs on")):
    """
    Serve the documentation using MkDocs with the project's configuration.

    Args:
        port (str): The port to serve the docs on. Defaults to "8000".
    """
    # Get the root directory of the project
    project_root = get_project_root(os.getcwd())
    if project_root is None:
        typer.echo("Error: Could not find the root of the iterative project.")
        raise typer.Exit(code=1)

    # Generate or update the mkdocs.yml configuration for the project
    doc_utils.update_mkdocs_config_for_project(project_root)

    # Path to the mkdocs configuration file within the .iterative directory
    mkdocs_config_path = os.path.join(project_root, '.iterative', 'mkdocs.yml')

    # Check if the mkdocs configuration file exists
    if not os.path.exists(mkdocs_config_path):
        typer.echo(f"Error: MkDocs configuration file not found at {mkdocs_config_path}")
        raise typer.Exit(code=1)

    # Run the mkdocs serve command with the project's configuration
    subprocess.run(["mkdocs", "serve", "-f", mkdocs_config_path, "--dev-addr", f"0.0.0.0:{port}"])

