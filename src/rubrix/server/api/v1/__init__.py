from fastapi import APIRouter

from rubrix.server.api.v1.constants import API_VERSION
from rubrix.server.api.v1.handlers.datasets import __router__ as datasets

api_router = APIRouter(prefix="/datasets")

dependencies = []
for router in [datasets]:
    api_router.include_router(router, dependencies=dependencies)
