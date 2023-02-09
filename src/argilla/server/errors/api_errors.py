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

from fastapi import HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel

from argilla.server.commons import telemetry
from argilla.server.errors.adapter import exception_to_argilla_error
from argilla.server.errors.base_errors import ServerError

_LOGGER = logging.getLogger("argilla")


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
    @staticmethod
    async def common_exception_handler(request: Request, error: Exception):
        """Wraps errors as custom generic error"""
        argilla_error = exception_to_argilla_error(error)
        await telemetry.track_error(argilla_error, request=request)

        return await http_exception_handler(request, ServerHTTPException(argilla_error))
