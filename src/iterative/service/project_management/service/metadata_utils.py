def generate_directory_tree(startpath: str = '.') -> str:
    """
    Generates a string representing the tree structure of the directory,
    ignoring __pycache__ directories.

    Args:
        startpath (str): The starting directory path. Defaults to the current directory.

    Returns:
        str: A string representation of the directory tree.
    """
    tree = []

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d != '__pycache__']  # Ignore __pycache__
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.endswith('.pyc'):  # Optionally ignore .pyc files
                tree.append(f"{subindent}{f}")

    tree_str = '\n'.join(tree)
    logger.info(tree_str)

    return tree_str