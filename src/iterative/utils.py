from datetime import date, timezone
import datetime
from enum import Enum
import sys
from typing import List
import uuid
import json
from functools import wraps
import os
import importlib.util
from fastapi import Response
from requests import Response as RequestsResponse

import logging

from iterative.models.action import Action
from pydantic import BaseModel


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


def snake_case(s: str) -> str:
    return s.replace("-", "_").replace(" ", "_")

def load_module_from_path(path: str):
    # Add the directory containing 'models' to sys.path
    root_directory = find_iterative_root(os.getcwd())
    if root_directory not in sys.path:
        sys.path.insert(0, root_directory)

    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

        
def print_iterative():
    ascii_art = """
                                 ___           ___           ___                                                    ___     
       ___         ___          /  /\         /  /\         /  /\          ___            ___         ___          /  /\    
      /__/\       /__/\        /  /::\       /  /::\       /  /::\        /__/\          /__/\       /  /\        /  /::\   
      \__\:\      \  \:\      /  /:/\:\     /  /:/\:\     /  /:/\:\       \  \:\         \__\:\     /  /:/       /  /:/\:\  
      /  /::\      \__\:\    /  /::\ \:\   /  /::\ \:\   /  /::\ \:\       \__\:\        /  /::\   /  /:/       /  /::\ \:\ 
   __/  /:/\/      /  /::\  /__/:/\:\ \:\ /__/:/\:\_\:\ /__/:/\:\_\:\      /  /::\    __/  /:/\/  /__/:/  ___  /__/:/\:\ \:\
  /__/\/:/~~      /  /:/\:\ \  \:\ \:\_\/ \__\/~|::\/:/ \__\/  \:\/:/     /  /:/\:\  /__/\/:/~~   |  |:| /  /\ \  \:\ \:\_\/
  \  \::/        /  /:/__\/  \  \:\ \:\      |  |:|::/       \__\::/     /  /:/__\/  \  \::/      |  |:|/  /:/  \  \:\ \:\  
   \  \:\       /__/:/        \  \:\_\/      |  |:|\/        /  /:/     /__/:/        \  \:\      |__|:|__/:/    \  \:\_\/  
    \__\/       \__\/          \  \:\        |__|:|~        /__/:/      \__\/          \__\/       \__\::::/      \  \:\    
                                \__\/         \__\|         \__\/                                      ~~~~        \__\/    
    """
    print(ascii_art + " : By Colorfull")
    already_printed = True