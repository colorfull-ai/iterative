from iterative.actions.assistant_actions import create_function_tool_from_callable, create_function_tool_from_endpoint, give_assistant_tools, parse_fastapi_app, parse_typer_app
import pytest
from typer import Typer
from fastapi import FastAPI, APIRouter

# Assuming the AssistantManager and other classes are already defined as above

# Mock functions and endpoints for testing
def mock_function(name: str, value: int):
    """
    A mock function for testing.
    """
    return value

def mock_endpoint():
    """
    A mock FastAPI endpoint for testing.
    """
    return {"message": "Hello, World!"}

# Test for parsing Typer app
def test_parse_typer_app():
    app = Typer()
    app.command(name="test_command")(mock_function)
    functions = parse_typer_app(app)
    assert len(functions) == 1
    assert functions[0]["function"]["name"] == "test_command"
    assert "value" in functions[0]["function"]["parameters"]["properties"]

# Test for parsing FastAPI app
def test_parse_fastapi_app():
    app = FastAPI()
    router = APIRouter()
    router.add_api_route("/test", mock_endpoint, methods=["GET"])
    app.include_router(router)
    functions = parse_fastapi_app(app)
    print(functions)
    assert len(functions) == 1
    assert functions[0]["function"]["name"] == "mock_endpoint"
    assert functions[0]["function"]["description"] == mock_endpoint.__doc__

# Test for creating function tool from callback
def test_create_function_tool_from_callback():
    function_tool = create_function_tool_from_callable("mock_function", mock_function)
    assert function_tool["function"]["name"] == "mock_function"
    assert "value" in function_tool["function"]["parameters"]["properties"]

# Test for creating function tool from endpoint
def test_create_function_tool_from_endpoint():
    app = FastAPI()
    router = APIRouter()
    router.add_api_route("/test", mock_endpoint, methods=["GET"])
    app.include_router(router)
    route = next(iter(app.routes))
    function_tool = create_function_tool_from_endpoint(route)
    assert function_tool["function"]["name"] == "mock_endpoint"
    assert function_tool["function"]["description"] == mock_endpoint.__doc__

# Integration test for give_assistant_tools
def test_give_assistant_tools():
    cli_app = Typer()
    cli_app.command(name="test_command")(mock_function)

    web_app = FastAPI()
    router = APIRouter()
    router.add_api_route("/test", mock_endpoint, methods=["GET"])
    web_app.include_router(router)

    tools = give_assistant_tools(cli_app, web_app)
    assert len(tools) == 2  # One from CLI and one from Web API
