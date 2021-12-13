#  coding=utf-8
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

from typing import Optional, Type

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel, ValidationError


class ErrorMessage(BaseModel):
    """
    Generic error class. This class is needed only for openapi documentation
    purposes.

    If some field in additional http errors changes, these changes
    should be reflected in the error model.

    Attributes:
    -----------

    detail:
        The error message

    """

    detail: str


class UnauthorizedError(HTTPException):
    """Unauthorized error"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(HTTPException):
    """Inactive user error"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )


class ForbiddenOperationError(HTTPException):
    """Forbidden operation"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message or "Operation not allowed",
        )


class BadRequestError(HTTPException):
    """Generic bad request error"""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


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


class EntityAlreadyExistsError(HTTPException):
    """Error raised when entity was created"""

    def __init__(self, name: str, type: Type, workspace: Optional[str] = None):
        self.name = name
        self.type = Type
        self.workspace = workspace

        msg = f"Already created entity {name} of type {type.__name__}"
        if self.workspace:
            msg += f" in {workspace} workspace."

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg,
        )


class EntityNotFoundError(HTTPException):
    """Error raised when entity not found"""

    def __init__(self, name: str, type: Type):
        self.name = name
        self.type = Type

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not found entity {name} of type {type.__name__}",
        )


class GenericValidationError(HTTPException):
    """Generic data validation error out of request"""

    def __init__(self, error: ValidationError):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(error.errors()),
        )


class GenericError(HTTPException):
    """Generic error"""

    def __init__(self, exception: Exception):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exception)
        )


async def common_exception_handler(request: Request, error: Exception):
    """Wraps errors as custom generic error"""
    return await http_exception_handler(request, GenericError(error))


async def validation_exception_handler(request: Request, error: ValidationError):
    """Wraps pydantic errors"""
    return await http_exception_handler(request, GenericValidationError(error))
