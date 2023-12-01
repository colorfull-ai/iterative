# src/iterative/cli.py

import typer
import os

app = typer.Typer()

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

# Usage
# iterative_root = find_iterative_root(os.getcwd())
# if iterative_root is not None:
#     print(f"Found Iterative root at: {iterative_root}")
# else:
#     print("No Iterative root found.")


import os

def main():
    app()

