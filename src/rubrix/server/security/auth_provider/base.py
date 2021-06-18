from typing import Optional

from fastapi.security import SecurityScopes
from rubrix.server.users.model import User


class AuthProvider:
    async def get_user(
        self, security_scopes: Optional[SecurityScopes], **kwargs
    ) -> User:
        raise NotImplementedError()

