from fastapi.security import (
    SecurityScopes,
)
from rubrix.server.users.model import MOCK_USER, User

class AuthProvider:
    """ Base class for auth provider"""
    async def get_user(self, security_scopes: SecurityScopes, **kwargs) -> User:
        raise NotImplementedError()


class MockAuthProvider(AuthProvider):
    async def get_user(self, security_scopes: SecurityScopes) -> User:
        return MOCK_USER
