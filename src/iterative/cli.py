# src/iterative/cli.py

import json
import os
import subprocess
import tempfile
from iterative.server_management import run_web_server
import typer

iterative_cli_app = typer.Typer()

@iterative_cli_app.command()
def start_server():
    run_web_server()

@iterative_cli_app.command()
def run_crud_ui(model_name: str):
    # Create a temporary file to store the model name
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as tmp:
        json.dump({'model_name': model_name}, tmp)
        tmp_filename = tmp.name

    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the path to the streamlit_app.py file
    streamlit_app_path = os.path.join(current_dir, "ui", "crud_ui.py")

    # Call the Streamlit run command as a subprocess
    subprocess.run(["streamlit", "run", streamlit_app_path, "--", tmp_filename])
