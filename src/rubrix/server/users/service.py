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

    def get_user(self, username) -> Optional[User]:
        return self.__dao__.get_user(username)

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
