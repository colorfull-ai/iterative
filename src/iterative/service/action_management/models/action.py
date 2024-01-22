import inspect
import uuid
from typing import Any, Callable, Dict
from iterative.service.model_management.models.iterative import IterativeModel
from pydantic import Field


class Action(IterativeModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    function: Callable
    file_path: str
    category: str

    # make getters and setters for name, function, file, script_source
    # name
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    # function
    def get_function(self):
        return self.function
    
    def set_function(self, function):
        self.function = function

    # file
    def get_file(self):
        return self.file_path
    
    def set_file(self, file):
        self.file_path = file

    # script_source
    def get_category(self):
        return self.category
    
    def set_script_source(self, script_source):
        self.category = script_source

    def to_json(self) -> Dict[str, Any]:
        function_tool = create_function_tool_from_callback(self.name, self.function)
        return {
            "type": "action",
            "action": {
                "name": self.get_name(),
                "file": self.get_file(),
                "function": function_tool['function'],
                "script_source": self.get_category()
            }
        }
    
# Helper function to create a JSON representation from a function callback
def create_function_tool_from_callback(name: str, callback: Callable) -> Dict[str, Any]:
    params = inspect.signature(callback).parameters
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in params.items():
        # Determine the type of the parameter
        param_type = "string"  # default type if no annotation is provided
        if param.annotation != inspect.Parameter.empty:
            param_type = param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
        
        # Determine the description of the parameter
        param_description = param_name  # default description is the name of the parameter
        # If the function has a docstring, you could potentially parse it for a description

        parameters["properties"][param_name] = {
            "type": param_type,
            "description": param_description
        }
        if param.default is param.empty:
            parameters["required"].append(param_name)

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": callback.__doc__ or "No description provided",
            "parameters": parameters
        }
    }