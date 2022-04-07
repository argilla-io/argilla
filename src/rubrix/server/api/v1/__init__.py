from fastapi import APIRouter

from rubrix.server.api.v1.constants import API_VERSION
from rubrix.server.api.v1.handlers.datasets import __router__ as datasets
from rubrix.server.api.v1.handlers.logging import __router__ as logging
from rubrix.server.api.v1.handlers.search import __router__ as search
from rubrix.server.api.v1.handlers.weak_supervision import (
    __router__ as weak_supervision,
)

api_router = APIRouter(prefix=f"/{API_VERSION}/datasets")
dependencies = []
for router in [datasets, logging, search, weak_supervision]:
    api_router.include_router(router, dependencies=dependencies)
