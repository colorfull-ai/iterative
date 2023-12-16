import os
import subprocess
from iterative.server_management import run_web_server
import typer

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


# Find all py scripts for streamlit apps (they should be stand alone)