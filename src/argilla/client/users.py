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

import warnings
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID

from pydantic import ValidationError

import argilla.client.sdk.users.api as users_api
from argilla.client import active_client
from argilla.client.sdk.commons.errors import AlreadyExistsApiError, BaseClientError
from argilla.server.models import UserRole as Roles

if TYPE_CHECKING:
    from argilla.client.sdk.users.models import UserModel


class User:
    username: str
    id: UUID
    first_name: str
    last_name: Optional[str]
    role: Roles
    workspaces: Optional[List[str]]
    api_key: str
    inserted_at: datetime
    updated_at: datetime

    def __init__(self, username: Optional[str] = None, *, id: Optional[str] = None) -> None:
        assert username or id, "Either the `username` or `id` must be provided."

        existing_user = self.__user_exists(username=username, id=id)
        if existing_user is None:
            raise ValueError(
                f"User with username=`{username}` and/or id=`{id}` doesn't exist in Argilla, so please create it first via the `User.create` method."
            )
        self.__dict__.update(existing_user.dict())

    @staticmethod
    def __user_exists(username: Optional[str] = None, id: Optional[str] = None) -> Optional["UserModel"]:
        # loop through `list_users` and look for matches on either `username` or `id`, if
        # the user exists return the reponse, otherwise return None
        for user in list_users():
            if user.username == username or user.id == id:
                return user
        return None

    def __str__(self) -> str:
        return f"User(id={self.id}, username={self.username}, role={self.role}, workspaces={self.workspaces}, api_key={self.api_key}, first_name={self.first_name}, last_name={self.last_name}, role={self.role}, inserted_at={self.inserted_at}, updated_at={self.updated_at})"

    def delete(self) -> None:
        users_api.delete_user(active_client().http_client.httpx, self.id)

    @classmethod
    def create(
        cls,
        username: str,
        password: Union[str, UUID],
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[Roles] = None,
    ) -> "User":
        if not first_name:
            warnings.warn(
                "Since the `first_name` hasn't been provided, it will be set to the same value as the `username`."
            )
            first_name = username
        if not role:
            warnings.warn("Since the `role` hasn't been provided, it will be set to `annotator`.")
            role = "annotator"

        if isinstance(password, UUID):
            warnings.warn("Since the `password` is a UUID, it will be converted to a string.")
            password = str(password)

        try:
            user = users_api.create_user(
                client=active_client().http_client.httpx,
                first_name=first_name,
                username=username,
                password=password,
                last_name=last_name,
                role=role,
            ).parsed
        except AlreadyExistsApiError as e:
            raise ValueError(
                f"User with username=`{username}` already exists, so please use a different username."
            ) from e
        except (ValidationError, BaseClientError) as e:
            raise e

        instance = cls.__new__(cls)
        instance.__dict__.update(user.dict())
        return instance

    @classmethod
    def me(cls) -> "User":
        user = users_api.whoami(active_client().http_client.httpx).parsed
        instance = cls.__new__(cls)
        instance.__dict__.update(user.dict())
        return instance


def list_users() -> List["UserModel"]:
    return users_api.list_users(active_client().http_client.httpx).parsed
