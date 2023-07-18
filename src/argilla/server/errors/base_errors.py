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

from typing import Any, Optional, Type, Union

import pydantic
from starlette import status


class ServerError(Exception):
    HTTP_STATUS: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def api_documentation(cls):
        return {
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "code": cls.get_error_code(),
                            "params": {"extra": "error parameters"},
                        }
                    }
                }
            },
        }

    @classmethod
    def get_error_code(cls):
        return f"argilla.api.errors::{cls.__name__}"

    @property
    def code(self) -> str:
        return self.get_error_code()

    @property
    def arguments(self):
        return {k: v for k, v in vars(self).items() if v is not None} if vars(self) else None

    def __str__(self):
        args = self.arguments or {}
        printable_args = ",".join([f"{k}={v}" for k, v in args.items()])
        return f"{self.code}({printable_args})"


class ValidationError(ServerError):
    """Generic data validation error out of request"""

    HTTP_STATUS = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, error: pydantic.ValidationError):
        self.model = error.model.__name__
        self.errors = error.errors()


class GenericServerError(ServerError):
    def __init__(self, error: Exception):
        self.type = f"{type(error).__module__}.{type(error).__name__}"
        self.message = str(error)
        self.args = error.args

    @classmethod
    def api_documentation(cls):
        return {
            "content": {"application/json": {"example": {"detail": {"code": "builtins.TypeError"}}}},
        }


class ForbiddenOperationError(ServerError):
    """Forbidden operation"""

    HTTP_STATUS = status.HTTP_403_FORBIDDEN

    def __init__(self, message: Optional[str] = None):
        self.detail = message or "Operation not allowed"


class UnauthorizedError(ServerError):
    """Unauthorized operation"""

    HTTP_STATUS = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message: Optional[str] = None):
        self.detail = message or "Could not validate credentials"


class BadRequestError(ServerError):
    """Generic bad request error"""

    HTTP_STATUS = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str):
        self.message = detail


class BulkDataError(BadRequestError):
    """Error on bulk data"""

    def __init__(self, detail: str, errors: Any):
        super().__init__(detail)
        self.errors = errors


class InactiveUserError(ServerError):
    """Inactive user error"""

    HTTP_STATUS = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        self.detail = "Inactive user"


class WrongInputParamError(BadRequestError):
    """Error related with input params in general"""

    pass


class InvalidTextSearchError(BadRequestError):
    """Error related with input params in search"""

    pass


class WrongTaskError(BadRequestError):
    """Error raised when provided task cannot be processed with requested entity"""

    pass


class MissingInputParamError(BadRequestError):
    """Error when some required parameter is missing for operation"""

    pass


class EntityAlreadyExistsError(ServerError):
    """Error raised when entity was created"""

    HTTP_STATUS = status.HTTP_409_CONFLICT

    def __init__(self, name: str, type: Type, workspace: Optional[str] = None):
        self.name = name
        self.type = type.__name__
        self.workspace = workspace


class EntityNotFoundError(ServerError):
    """Error raised when entity not found"""

    HTTP_STATUS = status.HTTP_404_NOT_FOUND

    def __init__(self, name: str, type: Union[Type, str]):
        self.name = name  # TODO: rename to id
        self.type = type if isinstance(type, str) else type.__name__


class RecordNotFound(EntityNotFoundError):
    def __init__(self, dataset: str, id: str, type: Union[Type, str]):
        self.dataset = dataset
        self.id = id

        super().__init__(
            name=f"{self.dataset}.{self.id}",
            type=type,
        )


class ClosedDatasetError(BadRequestError):
    def __init__(self, name: str):
        self.name = name


class MissingDatasetRecordsError(BadRequestError):
    def __init__(self, message: str):
        self.message = message


__ALL__ = [
    BadRequestError,
    EntityNotFoundError,
    ForbiddenOperationError,
    EntityAlreadyExistsError,
    ValidationError,
    GenericServerError,
    ClosedDatasetError,
    MissingDatasetRecordsError,
]
