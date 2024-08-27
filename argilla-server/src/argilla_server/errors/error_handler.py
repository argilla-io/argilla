#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError

from argilla_server.errors.base_errors import (
    BadRequestError,
    ClosedDatasetError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ForbiddenOperationError,
    GenericServerError,
    InvalidTextSearchError,
    MissingInputParamError,
    ServerError,
    UnauthorizedError,
    ValidationError,
    WrongTaskError,
)
from argilla_server.pydantic_v1 import BaseModel
from argilla_server.telemetry import get_telemetry_client


class ErrorDetail(BaseModel):
    code: str
    params: Dict[str, Any]


# TODO(@frascuchon): Review class Naming
class ServerHTTPException(HTTPException):
    def __init__(self, error: ServerError):
        super().__init__(
            status_code=error.HTTP_STATUS,
            detail=ErrorDetail(code=error.code, params=error.arguments).dict(),
        )


class APIErrorHandler:
    @classmethod
    async def track_error(cls, error: ServerError, request: Request):
        await get_telemetry_client().track_error(error=error, request=request)

    @classmethod
    async def common_exception_handler(cls, request: Request, error: Exception):
        """Wraps errors as custom generic error"""
        argilla_error = cls._exception_to_argilla_error(error)
        await cls.track_error(argilla_error, request=request)

        return await http_exception_handler(request, ServerHTTPException(argilla_error))

    @classmethod
    def configure_app(cls, app: FastAPI):
        """Configures fastapi exception handlers"""
        for exception_type in [
            AssertionError,
            BadRequestError,
            ClosedDatasetError,
            EntityNotFoundError,
            EntityAlreadyExistsError,
            Exception,
            UnauthorizedError,
            ForbiddenOperationError,
            InvalidTextSearchError,
            MissingInputParamError,
            RequestValidationError,
            ValidationError,
            WrongTaskError,
        ]:
            app.add_exception_handler(exception_type, APIErrorHandler.common_exception_handler)

    @classmethod
    def _exception_to_argilla_error(cls, error: Exception) -> ServerError:
        if isinstance(error, ServerError):
            return error

        _LOGGER.error(error, exc_info=error, stacklevel=2)
        if isinstance(error, RequestValidationError):
            return ValidationError(error)

        if isinstance(error, AssertionError):
            return BadRequestError(str(error))

        # TODO: here we can extend/specify more error adapters
        return GenericServerError(error=error)


_LOGGER = logging.getLogger("argilla")
