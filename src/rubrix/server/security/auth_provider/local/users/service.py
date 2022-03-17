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

from typing import Optional

from fastapi import Depends
from passlib.context import CryptContext

from rubrix.server.datasets.service import DatasetsService

from .dao import UsersDAO, create_users_dao
from .model import User


class UsersService:
    """Users management service"""

    __PWD_CONTEXT__ = CryptContext(schemes=["bcrypt"], deprecated="auto")

    __INSTANCE__: Optional["UsersService"] = None

    @classmethod
    def get_instance(
        cls,
        users: UsersDAO = Depends(create_users_dao),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
    ) -> "UsersService":
        if not cls.__INSTANCE__:
            cls.__INSTANCE__ = cls(users=users, datasets=datasets)
        return cls.__INSTANCE__

    def __init__(self, users: UsersDAO, datasets: DatasetsService):
        self.__dao__ = users
        self.__datasets__ = datasets

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
        user = self.__dao__.get_user(username)
        if user:
            user = self._enrich_user(user)
        return user

    def _enrich_user(self, user: User) -> User:
        if user.is_superuser():
            user.workspaces = self.__datasets__.all_workspaces()
        return user

    async def find_user_by_api_key(self, api_key: str) -> Optional[User]:
        user = await self.__dao__.get_user_by_api_key(api_key)
        if user:
            user = self._enrich_user(user)
        return user

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
