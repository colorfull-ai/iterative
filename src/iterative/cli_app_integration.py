from iterative.utils import snake_case, log_function_call

def integrate_actions_into_cli_app(actions, cli_app):
    for action in actions:
        snake_name = snake_case(action['name'])
        logged_func = log_function_call(action['function'])
        cli_app.command(name=snake_name)(logged_func)