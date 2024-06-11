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

from httpx import HTTPStatusError

from argilla._exceptions._base import ArgillaErrorBase


class ArgillaAPIError(ArgillaErrorBase):
    pass


class BadRequestError(ArgillaAPIError):
    message = "Bad request to the server"


class ForbiddenError(ArgillaAPIError):
    message = "Forbidden request to the server"


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
        raise exception_class(f"{exception_class.message}. Details: {error_detail}")

    def _handler_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPStatusError as e:
            _error_switch(status_code=e.response.status_code, error_detail=e.response.text)

    return _handler_wrapper
