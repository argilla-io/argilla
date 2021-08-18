"""
This module configures the api routes under /api prefix, and
set the required security dependencies if api security is enabled
"""
from fastapi import APIRouter
from rubrix.server.commons.errors import ErrorMessage

from .datasets import api as datasets
from .info import api as info
from .tasks import api as tasks
from .users import api as users

api_router = APIRouter(
    responses={
        "404": {"model": ErrorMessage, "description": "Item not found"},
        "500": {"model": ErrorMessage, "description": "Generic error"},
    }
)


dependencies = []

for router in [users.router, datasets.router, info.router, tasks.router]:
    api_router.include_router(router, dependencies=dependencies)
