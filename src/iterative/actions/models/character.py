from iterative import IterativeModel
from typing import *
from iterative.models import *

class Character(IterativeModel):
    _collection_name = "Character"
    # Add fields here
    description: str
