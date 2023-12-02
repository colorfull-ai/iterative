from typing import Callable
from iterative.models.iterative import IterativeModel

class Action(IterativeModel):
    name: str
    function: Callable
    file: str
    script_source: str

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
        return self.file
    
    def set_file(self, file):
        self.file = file

    # script_source
    def get_script_source(self):
        return self.script_source
    
    def set_script_source(self, script_source):
        self.script_source = script_source

        