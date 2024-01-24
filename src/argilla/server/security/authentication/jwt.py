from datetime import datetime, timedelta

from jose import JWTError, jwt

from argilla.server.errors import UnauthorizedError
from argilla.server.security.authentication.user import User
from argilla.server.security.settings import settings


class JWT:
    secret: str = settings.secret_key
    algorithm: str = settings.algorithm
    expires: int = settings.token_expire_time

    @classmethod
    def encode(cls, data: dict) -> str:
        return jwt.encode(data, cls.secret, algorithm=cls.algorithm)

    @classmethod
    def decode(cls, token: str) -> dict:
        try:
            return jwt.decode(token, cls.secret, algorithms=[cls.algorithm])
        except JWTError:
            raise UnauthorizedError("Invalid token")

    @classmethod
    def create(cls, user: User) -> str:
        expire = datetime.utcnow() + timedelta(seconds=cls.expires)
        return cls.encode({**user, "exp": expire})
