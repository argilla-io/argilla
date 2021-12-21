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

from fastapi import Depends
from passlib.context import CryptContext
from typing import Optional

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

    async def find_user_by_api_key(self, api_key: str) -> Optional[User]:
        return await self.__dao__.get_user_by_api_key(api_key)

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
