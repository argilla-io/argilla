from typing import Any, Dict, Optional, Type, Union

import pydantic
from starlette import status


class RubrixServerError(Exception):

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
        return f"rubrix.api.errors::{cls.__name__}"

    @property
    def code(self) -> str:
        return self.get_error_code()

    @property
    def arguments(self):
        return (
            {k: v for k, v in vars(self).items() if v is not None}
            if vars(self)
            else None
        )

    def __str__(self):
        args = self.arguments or {}
        printable_args = ",".join([f"{k}={v}" for k, v in args.items()])
        return f"{self.code}({printable_args})"


class ValidationError(RubrixServerError):
    """Generic data validation error out of request"""

    HTTP_STATUS = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, error: pydantic.ValidationError):
        self.model = error.model.__name__
        self.errors = error.errors()


class GenericRubrixServerError(RubrixServerError):
    def __init__(self, error: Exception):
        self.error = error

    @classmethod
    def api_documentation(cls):
        return {
            "content": {
                "application/json": {
                    "example": {"detail": {"code": "builtins.TypeError"}}
                }
            },
        }

    @classmethod
    def get_error_code(cls):
        raise NotImplementedError(
            "This class method is not supported for generic server error"
        )

    @property
    def code(self) -> str:
        return f"{type(self.error).__module__}.{type(self.error).__name__}"

    @property
    def arguments(self):
        return {}


class ForbiddenOperationError(RubrixServerError):
    """Forbidden operation"""

    HTTP_STATUS = status.HTTP_403_FORBIDDEN

    def __init__(self, message: Optional[str] = None):
        self.detail = message or "Operation not allowed"


class BadRequestError(RubrixServerError):
    """Generic bad request error"""

    HTTP_STATUS = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str):
        self.message = detail


class InactiveUserError(RubrixServerError):
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


class EntityAlreadyExistsError(RubrixServerError):
    """Error raised when entity was created"""

    HTTP_STATUS = status.HTTP_409_CONFLICT

    def __init__(self, name: str, type: Type, workspace: Optional[str] = None):
        self.name = name
        self.type = type.__name__
        self.workspace = workspace


class EntityNotFoundError(RubrixServerError):
    """Error raised when entity not found"""

    HTTP_STATUS = status.HTTP_404_NOT_FOUND

    def __init__(self, name: str, type: Union[Type, str]):
        self.name = name
        self.type = type if isinstance(type, str) else type.__name__


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
    GenericRubrixServerError,
    ClosedDatasetError,
    MissingDatasetRecordsError,
]
