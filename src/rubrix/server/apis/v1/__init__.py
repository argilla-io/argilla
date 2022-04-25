from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError

from rubrix.server.apis.v1.constants import API_VERSION
from rubrix.server.apis.v1.handlers.dataset_settings import (
    __router__ as dataset_settings,
)
from rubrix.server.apis.v1.handlers.datasets import __router__ as datasets

__v1_router__ = APIRouter(prefix="/datasets")

from rubrix.server.errors import APIErrorHandler
from rubrix.server.errors.base_errors import __ALL__ as ALL_ERRORS

dependencies = []
for router in [datasets, dataset_settings]:
    __v1_router__.include_router(router, dependencies=dependencies)


api_v1 = FastAPI(
    description="Rubrix API v1 **EXPERIMENTAL**",
    # Disable default openapi configuration
    redoc_url=None,
    version="v1",
    responses={error.HTTP_STATUS: error.api_documentation() for error in ALL_ERRORS},
)

api_v1.include_router(__v1_router__)
api_v1.exception_handler(Exception)(APIErrorHandler.common_exception_handler)
api_v1.exception_handler(RequestValidationError)(
    APIErrorHandler.common_exception_handler
)
