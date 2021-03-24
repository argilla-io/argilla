"""
This module configures the api routes under /api prefix, and
set the required security dependencies if api security is enabled
"""
from fastapi import APIRouter, Depends

from .datasets import api as datasets
from .security import api as security
from .security.settings import settings
from .snapshots import api as snapshots
from .text_classification import api as text_classification
from .token_classification import api as token_classification
from .users import api as users
from .info import api as info

api_router = APIRouter()

security_dependencies = [Depends(security.get_current_active_user)]
dependencies = [*security_dependencies]

for router in [
    users.router,
    datasets.router,
    text_classification.router,
    token_classification.router,
    snapshots.router,
    info.router,
]:
    api_router.include_router(router, dependencies=dependencies)

if settings.enable_security:
    api_router.include_router(security.router)
