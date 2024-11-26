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
from pydantic import BaseModel, field_serializer

from argilla_server.api.errors.v1.exception_handlers import set_request_error
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


class ErrorDetail(BaseModel):
    code: str
    params: Dict[str, Any]

    # TODO: Newer version does not serialize some exceptions such as ValueError
    @field_serializer("params")
    def serialize_params(self, value):
        return self._parse_to_serializable(value)

    @classmethod
    def _parse_to_serializable(cls, value: Any) -> Any:
        if isinstance(value, ValueError):
            return str(value)

        if isinstance(value, dict):
            for k in value:
                value[k] = cls._parse_to_serializable(value[k])
            return value

        if isinstance(value, list):
            return [cls._parse_to_serializable(item) for item in value]

        return value


# TODO(@frascuchon): Review class Naming
class ServerHTTPException(HTTPException):
    def __init__(self, error: ServerError):
        super().__init__(
            status_code=error.HTTP_STATUS,
            detail=ErrorDetail(code=error.code, params=error.arguments).model_dump(),
        )


class APIErrorHandler:
    @classmethod
    async def common_exception_handler(cls, request: Request, error: Exception):
        """Wraps errors as custom generic error"""
        argilla_error = cls._exception_to_argilla_error(error)
        set_request_error(request, argilla_error)

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
