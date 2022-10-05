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

from typing import List, Optional

from fastapi import Depends
from passlib.context import CryptContext

from argilla.server.daos.datasets import NO_WORKSPACE

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
    ) -> "UsersService":
        if not cls.__INSTANCE__:
            cls.__INSTANCE__ = cls(users=users)
        return cls.__INSTANCE__

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
        user = self.__dao__.get_user(username)
        if user and user.is_superuser():
            workspaces = list(self._fetch_all_workspaces())
            if NO_WORKSPACE not in workspaces:
                workspaces.append(NO_WORKSPACE)
            user.workspaces = workspaces
        return user

    def _fetch_all_workspaces(self) -> List[str]:
        return list(
            set(
                workspace
                for user in self.__dao__.all_users()
                for workspace in user.check_workspaces([])  # return ALL workspaces
            )
        )

    async def find_user_by_api_key(self, api_key: str) -> Optional[User]:
        user = await self.__dao__.get_user_by_api_key(api_key)
        if user and user.is_superuser():
            user.workspaces = [NO_WORKSPACE] + list(self._fetch_all_workspaces())
        return user

    def __verify_password__(self, password: str, hashed_password: str) -> bool:
        return self.__PWD_CONTEXT__.verify(password, hashed_password)

    def __get_password_hash__(self, password: str):
        return self.__PWD_CONTEXT__.hash(password)
