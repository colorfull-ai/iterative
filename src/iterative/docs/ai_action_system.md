Our system enables AI to interact and manipulate the codebase through a feature called "Actions." Actions are essentially functions that the AI can execute, and they are dynamically registered at runtime. This functionality allows the AI to contribute effectively to the development process.

**Key Components of Actions:**

1. **API Routers and Actions Directory:** By default, any public function defined in `.py` files within the `api` and `actions` folders is considered an action available to both the AI and the Command Line Interface (CLI). 

2. **Scalar Argument Design:** Our CLI is designed to work exclusively with scalar arguments (strings, integers, floats, booleans, or None). This limitation is ingeniously circumvented using a system inspired by Adobe Photoshop's Action System.

3. **`execute_action_calls` Function:** This central function plays a pivotal role. It accepts a JSON string that represents a series of function calls, each with its respective arguments. The function executes these calls in the order they are provided.

   For example, here's a JSON payload that could be used with `execute_action_calls`:

   ```python
   [
     {"function": "add_property_to_model", "args": {"entity_name": "world_element", "property_name": "historical_event", "property_type": "str"}},
     // ... more function calls
   ]
   ```

   This function iteratively processes each command, ensuring that the specified function is available and then executes it with the provided arguments.

**Project Flow and Structure:**

- The `actions` and `api` folders primarily contain public logic, allowing for code manipulation and interaction.
- The `service` folder in an iterative project is the core, housing the bulk of the service logic.
- Both `actions` and `api` serve as interfaces to interact with and manipulate the service layer through coding and user interactions.

**Documentation and Maintenance:**

- To facilitate ongoing service maintenance, the AI (or assistant) is provided with the necessary `actions` and comprehensive documentation.
- The `docs` folder is crucial, containing detailed information about the service, including maintenance guidelines, known issues, quirks, etc., for both users and AI.

By adopting this structure, we ensure that both the AI and users have a clear understanding of the system's functionality and maintenance requirements. This approach streamlines development, allowing for efficient interaction and manipulation of the service layer.

## Describing action calling further

We have a function called `execute_action_calls` that takes in a json string and calls the releveant functions int he order it received the functions and arguments int he json

this would be a payload it would give for the `execute_action_calls`

```python
[
  {
    "function": "add_property_to_model",
    "args": {
      "entity_name": "world_element",
      "property_name": "historical_event",
      "property_type": "str"
    }
  },
  {
    "function": "add_property_to_model",
    "args": {
      "entity_name": "world_element",
      "property_name": "location_description",
      "property_type": "str"
    }
  },
  {
    "function": "add_property_to_model",
    "args": {
      "entity_name": "character",
      "property_name": "related_event",
      "property_type": "str"
    }
  },
  {
    "function": "add_property_to_model",
    "args": {
      "entity_name": "character",
      "property_name": "origin_location",
      "property_type": "str"
    }
  }
]

```

this is that function


def execute_action_calls(json_commands):
    """
    Execute a series of function calls defined by a JSON-formatted string.
    
    The JSON string should be a serialized array of command objects. Each command object
    must contain two keys:
    
    'function': A string that specifies the name of the function to call.
                The function must exist in the global scope and be callable.
                
    'args': A dictionary where each key-value pair represents an argument name and its
            corresponding scalar value (i.e., string, integer, float, boolean, or None) to
            pass to the function. The function will be called with these arguments.
            
    All functions and arguments must be defined such that they are compatible with scalar values
    only, as complex types are not supported in this interface.
    
    Example of a valid JSON string:
    
    ```
    [
      {
        "function": "update_project_config_value",
        "args": {"key": "database_port", "value": 5432}
      },
      {
        "function": "enable_feature",
        "args": {"feature_name": "logging", "status": true}
      },
      // Add more function calls as needed
    ]
    ```
    
    Args:
        json_commands (str): A JSON string representing an ordered list of function calls
                             and their scalar arguments. The commands will be executed in
                             the order they appear in the string.
                             
    Raises:
        json.JSONDecodeError: If `json_commands` is not a valid JSON string.
        Exception: For any issues during function execution, including if a function is not
                   found, or if there is a mismatch between provided arguments and the
                   function's parameters.
    """
    try:
        # Deserialize the JSON string into a Python object
        commands = json.loads(json_commands)
        
        # Iterate over the list of commands
        for command in commands:
            function_name = command['function']
            args = command['args']

            # Ensure the function exists and is callable
            function_to_call = globals().get(function_name)
            if callable(function_to_call):
                # Execute the function with the provided arguments
                function_to_call(**args)
            else:
                logger.error(f"Function {function_name} not found or is not callable.")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except Exception as e:
        logger.error(f"Error executing function calls: {e}")


The flow of the project is meant the have `actions` and `api` have mostly public logic while the `service` folder in an `iterative` project is supposed to hold the bulk of the service.  `actions` and `api` are ways to manipulate the `service` via coding and interaction.

The id would be that to maintain this service, you would provide the `assistant`, or `AI`, with the `actions` required to maintain it as well as the knowledge it would need which would be in the `docs` folder. More on that later, but we put docs in that folder to give more context around the service, maintenance, issues, quirks, to both `users`` and `AI`




