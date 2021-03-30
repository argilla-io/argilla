from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from rubrix.server.security.settings import settings

from .dao import UsersDAO, create_users_dao
from .model import User


class UsersService:
    """Users management service"""

    __PWD_CONTEXT__ = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, users: UsersDAO):
        self.__dao__ = users

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticates an user given username/password

        Parameters
        ----------
        username:
            The user name
        password:
            The password

        Returns
        -------
            An user instance if authentication success. None otherwise

        """
        user = self.__dao__.get_user(username)
        if user and self.__verify_password__(password, user.hashed_password):
            return user

    @staticmethod
    def create_access_token(
        username: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates an access token

        Parameters
        ----------
        username:
            The user name
        expires_delta:
            Token expiration

        Returns
        -------
            An access token string
        """
        to_encode = {
            "sub": username,
            "exp": datetime.utcnow() + (expires_delta or timedelta(minutes=15)),
        }
        return jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def fetch_token_user(self, token: str) -> Optional[User]:
        """
        Fetch the user for a given access token

        Parameters
        ----------
        token:
            The access token

        Returns
        -------
            An User instance if a valid token was provided. None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
            username: str = payload.get("sub")
            if username:
                return self.__dao__.get_user(user_name=username)
        except JWTError:
            return None

    def __verify_password__(self, password: str, hashed_password: str) -> bool:
        return self.__PWD_CONTEXT__.verify(password, hashed_password)

    def __get_password_hash__(self, password: str):
        return self.__PWD_CONTEXT__.hash(password)


_instance: Optional[UsersService] = None


def create_users_service(dao: UsersDAO = Depends(create_users_dao)) -> UsersService:
    """
    Creates an users service instance

    Parameters
    ----------
    dao:
        The users data access object

    Returns
    -------
        An service instance
    """
    global _instance

    if _instance is None:
        _instance = UsersService(users=dao)
    return _instance
