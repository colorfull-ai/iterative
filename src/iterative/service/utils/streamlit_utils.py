import importlib
import os
import sys

from iterative.service.utils.project_utils import get_project_root


def import_main_from_script(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return getattr(module, 'main', None)


def find_streamlit_scripts(in_current_project=True):
    if in_current_project:
        root_path = get_project_root()

    streamlit_scripts = {}
    streamlit_path = os.path.join(root_path, 'streamlits')

    for root, dirs, files in os.walk(streamlit_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                main_function = import_main_from_script(file_path)
                if main_function:
                    script_name = os.path.splitext(file)[0].replace('_', ' ').title()
                    streamlit_scripts[script_name] = main_function
    return streamlit_scripts

