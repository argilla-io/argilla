"""
This module configures the api routes under /api prefix, and
set the required security dependencies if api security is enabled
"""
from fastapi import APIRouter, Depends
from rubrix.server.commons.errors import ErrorMessage

from .datasets import api as datasets
from .info import api as info
from .security import api as security
from .security.settings import settings
from .snapshots import api as snapshots
from .tasks import api as tasks
from .users import api as users

api_router = APIRouter(
    responses={
        "404": {"model": ErrorMessage, "description": "Item not found"},
        "500": {"model": ErrorMessage, "description": "Generic error"},
    }
)


security_dependencies = [Depends(security.get_current_active_user)]
dependencies = [*security_dependencies]

for router in [
    users.router,
    datasets.router,
    # text_classification.router,
    # token_classification.router,
    tasks.router,
    snapshots.router,
    info.router,
]:
    api_router.include_router(router, dependencies=dependencies)

if settings.enable_security:
    api_router.include_router(security.router)
