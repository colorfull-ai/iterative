import os
import shutil
import typer
from iterative.cli import app

@app.command()
def init(func_name):
    """
    Initialize a new iterative app by copying the contents of a specific template directory to the current working directory.

    Args:
        template_name (str): The name of the template to be initialized.
    """
    func_name = func_name
    template_name = "starter"

    # Define the paths
    package_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(package_dir)
    template_dir = os.path.join(parent_dir, 'templates', func_name, template_name)
    target_dir = os.getcwd()

    # Check if the template directory exists
    if not os.path.exists(template_dir):
        typer.echo(f"Template '{template_name}' not found at {template_dir}")
        raise typer.Exit(code=1)

    try:
        # Copy each item from the template directory to the target directory
        for item in os.listdir(template_dir):
            source_item = os.path.join(template_dir, item)
            target_item = os.path.join(target_dir, item)

            # If it's a directory, use shutil.copytree, else use shutil.copy
            if os.path.isdir(source_item):
                shutil.copytree(source_item, target_item, dirs_exist_ok=True)
            else:
                shutil.copy(source_item, target_item)

        typer.echo(f"Initialized new iterative app with contents from template '{template_name}' in {target_dir}")
    except Exception as e:
        typer.echo(f"Error initializing app with template '{template_name}': {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
