#!/usr/bin/env python3
import subprocess
import re
import toml
from pathlib import Path

def run_cmd(cmd):
    """Run a shell command and return its output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_staged_changes():
    """Get all staged files and their content"""
    # Get list of staged files
    staged_files = run_cmd("git diff --cached --name-only")
    return staged_files.split('\n') if staged_files else []

def analyze_changes():
    """Analyze the changes to determine version bump type"""
    # Get the last tag
    last_tag = run_cmd("git describe --tags --abbrev=0 2>/dev/null || echo v0.0.0")
    
    # Get staged changes
    staged_files = get_staged_changes()
    if not staged_files or staged_files == ['']:
        return None
    
    # Get the staged commit message from the prepared commit msg
    commit_msg = ""
    commit_msg_file = Path(".git/COMMIT_EDITMSG")
    if commit_msg_file.exists():
        commit_msg = commit_msg_file.read_text()
    
    # Check for breaking changes
    if "BREAKING CHANGE:" in commit_msg or "!" in commit_msg:
        return "major"
    
    # Check for feature additions
    if commit_msg.startswith("feat"):
        return "minor"
    
    # Count file changes
    py_changes = sum(1 for f in staged_files if f.endswith('.py'))
    test_changes = sum(1 for f in staged_files if 'test' in f)
    doc_changes = sum(1 for f in staged_files if f.endswith(('.md', '.rst', '.txt')))
    
    # If there are Python file changes (excluding tests), consider it a patch
    if py_changes > 0 and not (test_changes == py_changes):
        return "patch"
    
    # If only documentation changed, no version bump needed
    if doc_changes == len(staged_files):
        return None
    
    # Default to patch for any other changes
    return "patch" if staged_files else None

def update_version(bump_type):
    """Update version in pyproject.toml"""
    if not bump_type:
        return
        
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return
    
    # Read current version
    data = toml.load(pyproject_path)
    current_version = data['tool']['poetry']['version']
    
    # Parse version components
    major, minor, patch = map(int, current_version.split('.'))
    
    # Update version based on bump type
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    
    # Update version in pyproject.toml
    new_version = f"{major}.{minor}.{patch}"
    data['tool']['poetry']['version'] = new_version
    
    # Write back to file
    with open(pyproject_path, 'w') as f:
        toml.dump(data, f)
    
    # Stage the updated pyproject.toml
    run_cmd("git add pyproject.toml")
    
    print(f"Version bumped from {current_version} to {new_version}")

def main():
    bump_type = analyze_changes()
    if bump_type:
        update_version(bump_type)

if __name__ == "__main__":
    main() 