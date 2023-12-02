import os
import shutil
import typer
import subprocess

app = typer.Typer()

@app.command()
def run_chat_ui():
    """
    Run the Streamlit chat application.
    """
    # Assuming your Streamlit app is in 'streamlit_app.py'
    subprocess.run(["streamlit", "run", "streamlit_app.py"])


