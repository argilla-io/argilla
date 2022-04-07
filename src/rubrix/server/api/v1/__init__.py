from fastapi import APIRouter

from rubrix.server.api.v2.handlers.datasets import __router__ as datasets
from rubrix.server.api.v2.handlers.logging import __router__ as logging
from rubrix.server.api.v2.handlers.search import __router__ as search
from rubrix.server.api.v2.handlers.weak_supervision import (
    __router__ as weak_supervision,
)

api_router = APIRouter(prefix="/v2/datasets")
dependencies = []
for router in [datasets, logging, search, weak_supervision]:
    api_router.include_router(router, dependencies=dependencies)
