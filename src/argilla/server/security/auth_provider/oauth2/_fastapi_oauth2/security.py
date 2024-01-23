from typing import Optional
from typing import Type

from fastapi.security import OAuth2 as FastAPIOAuth2
from fastapi.security import OAuth2AuthorizationCodeBearer as FastAPICodeBearer
from fastapi.security import OAuth2PasswordBearer as FastAPIPasswordBearer
from starlette.datastructures import Headers
from starlette.requests import Request


class OAuth2Cookie(type):
    """OAuth2 classes using this metaclass will use cookies for the Authorization header."""

    def __new__(metacls, name, bases, attrs) -> Type:
        instance = super().__new__(metacls, name, bases, attrs)

        async def __call__(self: FastAPIOAuth2, request: Request) -> Optional[str]:
            authorization = request.headers.get("Authorization", request.cookies.get("Authorization"))
            if authorization:
                request._headers = Headers({**request.headers, "Authorization": authorization})
            return await instance.__base__.__call__(self, request)

        instance.__call__ = __call__
        return instance


class OAuth2(FastAPIOAuth2, metaclass=OAuth2Cookie):
    """Wrapper class of the `fastapi.security.OAuth2` class."""


class OAuth2PasswordBearer(FastAPIPasswordBearer, metaclass=OAuth2Cookie):
    """Wrapper class of the `fastapi.security.OAuth2PasswordBearer` class."""


class OAuth2AuthorizationCodeBearer(FastAPICodeBearer, metaclass=OAuth2Cookie):
    """Wrapper class of the `fastapi.security.OAuth2AuthorizationCodeBearer` class."""
