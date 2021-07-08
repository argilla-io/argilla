from pydantic import BaseModel
from typing import List, Optional
from fastapi.security import (
    SecurityScopes,
)


class User(BaseModel):
    """Base user model"""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    user_groups: List[str] = None

    @property
    def current_group(self) -> Optional[str]:
        return self.user_groups[0] if self.user_groups else None


MOCK_USER = User(username=".local-Rubrix", disabled=False)


class AuthProvider:
    """Base class for auth provider"""

    async def get_user(self, security_scopes: SecurityScopes, **kwargs) -> User:
        raise NotImplementedError()


class MockAuthProvider(AuthProvider):
    async def get_user(self, security_scopes: SecurityScopes) -> User:
        return MOCK_USER
