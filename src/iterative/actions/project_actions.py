from iterative.service.project_management.service.template_utils import init_project as _init_project
from logging import getLogger as _getLogger

logger = _getLogger(__name__)

def init():
    logger.info("Starting to initialize project.")
    _init_project()
    logger.info("Successfully initialized project.")