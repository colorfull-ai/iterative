def create_relative_import_path(model_file_path: str, parent_project_root: str):
    """
    This function creates a relative import path from the parent project root to the model file path.
    """
    # Construct the relative import path from the last project root to the model file path
    relative_path_from_parent_to_model = os.path.relpath(
        model_file_path, parent_project_root
    ).replace(os.sep, ".")

    # Get the last part of the last_project_root (which is the project's name)
    last_project_name = os.path.basename(parent_project_root)

    # Prepend the project's name to the model_relative_path
    relative_path_from_parent_to_model = f"{last_project_name}.{relative_path_from_parent_to_model}"

    # Remove the '.py' extension from the import path
    relative_path_from_parent_to_model = relative_path_from_parent_to_model.rsplit('.', 1)[0]

    return relative_path_from_parent_to_model