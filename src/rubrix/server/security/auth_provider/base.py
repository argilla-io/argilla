from fastapi import Depends
from fastapi.security import (
    APIKeyHeader,
    SecurityScopes,
)
from rubrix._constants import API_KEY_HEADER_NAME
from rubrix.server.security.model import User
from typing import Optional


api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


class AuthProvider:
    """Base class for auth provider"""

    async def get_user(
        self,
        security_scopes: SecurityScopes,
        api_key: Optional[str] = Depends(api_key_header),
        **kwargs
    ) -> User:
        raise NotImplementedError()
