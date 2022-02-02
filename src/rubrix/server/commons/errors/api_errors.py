import logging
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel

from rubrix.server.commons.errors.adapter import exception_to_rubrix_error
from rubrix.server.commons.errors.base_errors import RubrixServerError

_LOGGER = logging.getLogger("rubrix")


class UnauthorizedError(HTTPException):
    """Unauthorized error"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RubrixErrorDetail(BaseModel):
    code: str
    params: Dict[str, Any]


class RubrixServerHTTPException(HTTPException):
    def __init__(self, error: RubrixServerError):
        super().__init__(
            status_code=error.HTTP_STATUS,
            detail=RubrixErrorDetail(code=error.code, params=error.arguments).dict(),
        )


class APIErrorHandler:
    @staticmethod
    async def common_exception_handler(request: Request, error: Exception):
        """Wraps errors as custom generic error"""
        rubrix_error = exception_to_rubrix_error(error)
        return await http_exception_handler(
            request, RubrixServerHTTPException(rubrix_error)
        )
