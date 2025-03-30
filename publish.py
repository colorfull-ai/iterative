#!/usr/bin/env python3
import subprocess
import sys
import os
import re
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return its output"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def update_version(version_bump='patch'):
    """Update the version using poetry"""
    valid_bumps = ['major', 'minor', 'patch']
    if version_bump not in valid_bumps:
        print(f"Invalid version bump type. Must be one of: {', '.join(valid_bumps)}")
        sys.exit(1)
    
    # Get current version
    old_version = run_command("poetry version -s")
    print(f"Current version: {old_version}")
    
    # Bump version
    run_command(f"poetry version {version_bump}")
    new_version = run_command("poetry version -s")
    print(f"New version: {new_version}")
    
    return new_version

def build_and_publish():
    """Build and publish the package to PyPI"""
    # Clean up any existing builds
    print("Cleaning up previous builds...")
    run_command("rm -rf dist/ build/ *.egg-info")
    
    # Build the package
    print("Building package...")
    run_command("poetry build")
    
    # Check if PYPI_TOKEN environment variable is set
    if "PYPI_TOKEN" not in os.environ:
        print("Error: PYPI_TOKEN environment variable not set")
        print("Please set it with: export PYPI_TOKEN=your_token_here")
        sys.exit(1)
    
    # Configure poetry with PyPI token
    print("Configuring PyPI token...")
    run_command(f"poetry config pypi-token.pypi {os.environ['PYPI_TOKEN']}")
    
    # Publish to PyPI
    print("Publishing to PyPI...")
    run_command("poetry publish")

def main():
    # Parse command line arguments
    version_bump = 'patch'  # default
    if len(sys.argv) > 1:
        version_bump = sys.argv[1]
    
    # Update version
    new_version = update_version(version_bump)
    
    # Build and publish
    build_and_publish()
    
    # Create and push git tag
    print("Creating and pushing git tag...")
    run_command(f"git tag v{new_version}")
    run_command("git push --tags")
    
    print(f"\nSuccessfully published version {new_version} to PyPI!")
    print("Package can now be installed with:")
    print(f"pip install iterative=={new_version}")

if __name__ == "__main__":
    main() 