from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError

from rubrix.server.api.v1.constants import API_VERSION
from rubrix.server.api.v1.handlers.datasets import __router__ as datasets
from rubrix.server.commons.errors import APIErrorHandler
from rubrix.server.commons.errors.base_errors import ALL_ERRORS

__v1_router__ = APIRouter(prefix="/datasets")

dependencies = []
for router in [datasets]:
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
