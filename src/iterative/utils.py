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


def snake_case(s: str) -> str:
    return s.replace("-", "_").replace(" ", "_")

def load_module_from_path(path: str):
    # Derive a module name from the file path
    module_name = os.path.splitext(os.path.basename(path))[0]

    # Add the directory containing the module to sys.path
    module_dir = os.path.dirname(path)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    spec = importlib.util.spec_from_file_location(module_name, path)
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