from logging import getLogger as _getLogger
from iterative.service.api_management.service.api_utils import (
    fetch_web_api_routes as _fetch_web_api_routes,
    generate_endpoints_for_model as _generate_endpoints_for_model,
)

logger = _getLogger(__name__)


def generate_model_endpoints(model_name: str):
    """
    Generate the API endpoints for a specific model.

    Args:
        model_name (str): The name of the model for which the API endpoints are to be generated.

    Returns:
        None

    Raises:
        ValueError: If the model name is not provided.
    """
    if not model_name:
        raise ValueError("Model name must be provided")

    _generate_endpoints_for_model(model_name)
