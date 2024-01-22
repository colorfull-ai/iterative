from typing import List
from iterative.service.action_management.models.action import Action
from iterative.service.project_management.service.project_utils import snake_case
from typer import Typer

def integrate_actions_into_cli_app(actions: List[Action], cli_app: Typer):
    for action in actions:
        name = action.get_name()
        function = action.get_function()
        snake_name = snake_case(name)
        cli_app.command(name=snake_name)(function)