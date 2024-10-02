# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Optional

from httpx import HTTPStatusError

from argilla._exceptions._base import ArgillaError


class ArgillaAPIError(ArgillaError):
    message = "Server error"

    def __init__(self, message: Optional[str] = None, status_code: int = 500):
        """Base class for all Argilla API exceptions
        Args:
            message (str): The message to display when the exception is raised
            status_code (int): The status code of the response that caused the exception
        """
        super().__init__(message)
        self.status_code = status_code


class BadRequestError(ArgillaAPIError):
    message = "Bad request to the server"


class ForbiddenError(ArgillaAPIError):
    message = "User role is forbidden from performing this action by server"


class NotFoundError(ArgillaAPIError):
    message = "Resource or entity not found on the server"


class ConflictError(ArgillaAPIError):
    message = "Conflict with the server. Resource or entity already exists"


class UnprocessableEntityError(ArgillaAPIError):
    message = "Unprocessable entity. The server cannot process the request"


class InternalServerError(ArgillaAPIError):
    message = "Internal server error"


class UnauthorizedError(ArgillaAPIError):
    message = "Unauthorized user request to the server"


def api_error_handler(func):
    """Decorator to handle API errors from ResourceAPI methods
    and raise the appropriate exception.
    Args: func: the request method to decorate

    Example:
    ```python

    @api_error_handler
    def get(self, workspace_id: UUID) -> WorkspaceModel:
        ... # same code as before
    ```
    """

    def _error_switch(status_code: int, error_detail: str):
        switch = {
            400: BadRequestError,
            401: UnauthorizedError,
            403: ForbiddenError,
            404: NotFoundError,
            409: ConflictError,
            422: UnprocessableEntityError,
            500: InternalServerError,
        }
        exception_class = switch.get(status_code, ArgillaAPIError)
        raise exception_class(f"{exception_class.message}. Details: {error_detail}", status_code=status_code)

    def _handler_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPStatusError as e:
            _error_switch(status_code=e.response.status_code, error_detail=e.response.text)

    return _handler_wrapper
