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
from typing import TYPE_CHECKING, Iterator, List, Optional, Union
from uuid import UUID

from argilla_v1.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    BaseClientError,
    NotFoundApiError,
    ValidationApiError,
)
from argilla_v1.client.sdk.users import api as users_api
from argilla_v1.client.sdk.users.models import UserModel, UserRole
from argilla_v1.client.sdk.v1.users import api as users_api_v1
from argilla_v1.client.sdk.v1.workspaces import api as workspaces_api_v1
from argilla_v1.client.singleton import active_client
from argilla_v1.client.utils import allowed_for_roles

if TYPE_CHECKING:
    import httpx

    from argilla_v1.client.sdk.client import AuthenticatedClient
    from argilla_v1.client.sdk.v1.workspaces.models import WorkspaceModel


class User:
    """The `User` class is used to manage users in Argilla. It provides methods to
    create new users, list all the users, get a user by its name or ID, and delete it.
    While it's not allowed to update the user information for the moment.

    Args:
        name: the name of the user to be managed. Defaults to None.
        id: the ID of the user to be managed. Defaults to None.

    Attributes:
        _client: the `httpx.Client` initialized to interact with the Argilla API.
        id: the ID of the user.
        username: the username of the user.
        first_name: the first name of the user.
        last_name: the last name of the user. Defaults to None.
        full_name: the full name of the user. Defaults to None.
        role: the role of the user.
        api_key: the API key of the user.
        inserted_at: the datetime when the user was created.
        updated_at: the datetime when the user was last updated.

    Examples:
        >>> from argilla_v1 import rg
        >>> user = rg.User.from_name("my-user") # or `User.from_id("...")`
        >>> print(user)
        User(id='...', username='my-user', role='annotator', first_name='Luke', last_name="Skywalker', full_name='Luke Skywalker', role='annotator', api_key='...', inserted_at=datetime.datetime(2021, 8, 31, 10, 0, 0), updated_at=datetime.datetime(2021, 8, 31, 10, 0, 0))
    """

    _client: "httpx.Client"  # Required to be able to use `allowed_for_roles` decorator
    username: str
    id: UUID
    first_name: str
    last_name: Optional[str]
    full_name: Optional[str]
    role: UserRole
    api_key: str
    inserted_at: datetime
    updated_at: datetime

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        id: Optional[Union[str, UUID]] = None,
    ) -> None:
        """Doesn't initialize the `User`, as it needs to be instantiated via any of
        the following classmethods, as the Argilla API is required.
            - `User.create` to create a new user in Argilla
            - `User.from_name` to get an existing user from Argilla by its name
            - `User.from_id` to get an existing user from Argilla by its ID
            - `User.list` to list all the users in Argilla

        Args:
            name: the name of the user to be managed. Defaults to None.
            id: the ID of the user to be managed. Defaults to None.

        Raises:
            Exception: if the `User` is initialized via the `__init__` method.
        """
        error_msg = (
            "`User` cannot be initialized via the `__init__` method, as it needs"
            " to send requests to the Argilla API, so it can just be instantiated via"
            " the following classmethods: `User.create`, `User.from_name`,"
            " `User.from_id` and `User.list`; note that it must exist in"
            " advance in Argilla, unless you are creating a new one."
        )
        if id is not None:
            error_msg += f" As the `id` argument is not None, you should use `User.from_id('{id}')` instead."
        if name is not None:
            error_msg += f" As the `name` argument is not None, you should use `User.from_name('{name}')` instead."
        raise Exception(error_msg)

    @property
    def workspaces(self) -> Optional[List["WorkspaceModel"]]:
        """Returns the workspace names the current user is linked to.

        Returns:
            A list of `WorkspaceModel` the current user is linked to.
        """
        connected_user = users_api.whoami_httpx(self._client).parsed
        if connected_user.role == UserRole.owner:
            return users_api_v1.list_user_workspaces(self._client, self.id).parsed
        return workspaces_api_v1.list_workspaces_me(self._client).parsed

    @property
    def is_owner(self) -> bool:
        """Returns whether the current user is an owner or not.

        Returns:
            A boolean indicating whether the current user is an owner or not.
        """
        return self.role == UserRole.owner

    @property
    def is_admin(self) -> bool:
        """Returns whether the current user is an admin or not.

        Returns:
            A boolean indicating whether the current user is an admin or not.
        """
        return self.role == UserRole.admin

    @property
    def is_annotator(self) -> bool:
        """Returns whether the current user is an annotator or not.

        Returns:
            A boolean indicating whether the current user is an annotator or not.
        """
        return self.role == UserRole.annotator

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username={self.username}, role={self.role},"
            f" api_key={self.api_key}, first_name={self.first_name},"
            f" last_name={self.last_name}, inserted_at={self.inserted_at},"
            f" updated_at={self.updated_at})"
        )

    @staticmethod
    def __active_client(httpx: bool = True) -> Union["httpx.Client", "AuthenticatedClient"]:
        """Returns the active Argilla `httpx.Client` instance."""
        try:
            client = active_client().http_client
            if httpx:
                client = client.httpx
            return client
        except Exception as e:
            raise RuntimeError("The `rg.active_client()` is not available or not responding.") from e

    @allowed_for_roles(roles=[UserRole.owner])
    def delete(self) -> None:
        """Deletes the user from Argilla.

        Raises:
            ValueError: if the user doesn't exist in Argilla.
            RuntimeError: if the user cannot be deleted from Argilla.

        Examples:
            >>> from argilla_v1 import rg
            >>> user = rg.User.from_name("my-user")
            >>> user.delete()
        """
        try:
            users_api.delete_user(self._client, user_id=self.id)
        except NotFoundApiError as e:
            raise ValueError(
                f"User with username=`{self.username}` doesn't exist in Argilla, so please"
                " make sure that the name you provided is a valid one."
            ) from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while deleting user with username=`{self.username}` from Argilla.") from e

    @classmethod
    def __new_instance(cls, client: Optional["httpx.Client"] = None, user: Optional["UserModel"] = None) -> "User":
        """Returns a new `User` instance."""
        instance = cls.__new__(cls)
        instance._client = client or cls.__active_client()
        if isinstance(user, UserModel):
            instance.__dict__.update(user.dict(exclude={"workspaces"}))
        return instance

    @classmethod
    @allowed_for_roles(roles=[UserRole.owner])
    def create(
        cls,
        username: str,
        password: str,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[UserRole] = None,
        workspaces: Optional[List[str]] = None,
    ) -> "User":
        """Creates a new user in Argilla.

        Args:
            username: the username of the user to be created.
            password: the password of the user to be created.
            first_name: the first name of the user to be created. Defaults to None.
            last_name: the last name of the user to be created. Defaults to None.
            role: the role of the user to be created. Defaults to None.
            workspaces: a list of workspace names the user to be created is linked to. Defaults to None.

        Returns:
            A new `User` instance.

        Raises:
            KeyError: if the user already exists in Argilla.
            ValueError: if the provided parameters are not valid.
            RuntimeError: if the user cannot be created in Argilla.

        Examples:
            >>> from argilla_v1 import rg
            >>> user = rg.User.create("my-user", "my-password", role="admin")
        """
        if not first_name:
            warnings.warn(
                "Since the `first_name` hasn't been provided, it will be set to the same value as the `username`."
            )
            first_name = username
        if not role:
            warnings.warn("Since the `role` hasn't been provided, it will be set to `annotator`.")
            role = UserRole.annotator

        client = cls.__active_client()
        try:
            user = users_api.create_user(
                client,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                workspaces=workspaces,
            ).parsed
            return cls.__new_instance(client, user)
        except AlreadyExistsApiError as e:
            raise KeyError(
                f"User with username=`{username}` already exists in Argilla, so please"
                " make sure that the name you provided is a unique one."
            ) from e
        except ValidationApiError as e:
            response = e.ctx["response"]
            raise ValueError(
                f"User with username=`{username}` cannot be created in Argilla, as"
                f" the provided data is not valid. Please, check the following error: {response}"
            ) from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while creating user with username=`{username}` in Argilla.") from e

    @classmethod
    @allowed_for_roles(roles=[UserRole.owner])
    def from_id(cls, id: UUID) -> "User":
        """Gets an existing user from Argilla by its ID.

        Args:
            id: the ID of the user to be retrieved.

        Returns:
            A `User` instance.

        Raises:
            ValueError: if the user with the provided ID doesn't exist.
            RuntimeError: if there was an error while retrieving the user.

        Examples:
            >>> from argilla_v1 import rg
            >>> user = rg.User.from_id("my-user")
        """
        client = cls.__active_client()
        try:
            users = users_api.list_users(client).parsed
            try:
                user = next(filter(lambda u: u.id == id, users))
            except StopIteration as e:
                raise ValueError(
                    f"User with id=`{id}` doesn't exist in Argilla, so please"
                    " make sure that the ID you provided is a valid one."
                ) from e
            return cls.__new_instance(client, user)
        except BaseClientError as e:
            raise RuntimeError(f"Error while retrieving user with id=`{id}` from Argilla.") from e

    @classmethod
    @allowed_for_roles(roles=[UserRole.owner])
    def from_name(cls, name: str) -> "User":
        """Gets an existing user from Argilla by its name.

        Args:
            name: the name of the user to be retrieved.

        Returns:
            A `User` instance.

        Raises:
            ValueError: if the user with the provided name doesn't exist.
            RuntimeError: if there was an error while retrieving the user.

        Examples:
            >>> from argilla_v1 import rg
            >>> user = rg.User.from_name("my-user")
        """
        client = cls.__active_client()
        try:
            users = users_api.list_users(client).parsed
            try:
                user = next(filter(lambda u: u.username == name, users))
            except StopIteration as e:
                raise ValueError(
                    f"User with username=`{name}` doesn't exist in Argilla, so please"
                    " make sure that the name you provided is a valid one."
                ) from e
            return cls.__new_instance(client, user)
        except NotFoundApiError as e:
            raise ValueError(
                f"User with username=`{name}` doesn't exist in Argilla, so please"
                " make sure that the name you provided is a valid one. Otherwise,"
                " you can create a new one via the `User.create` method."
            ) from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while retrieving user with username=`{name}` from Argilla.") from e

    @classmethod
    def me(cls) -> "User":
        """Gets the current user from Argilla.

        Returns:
            A `User` instance.

        Raises:
            RuntimeError: if there was an error while retrieving the current user.

        Examples:
            >>> from argilla_v1 import rg
            >>> user = rg.User.me()
        """
        client = cls.__active_client(httpx=False)
        try:
            user = users_api.whoami(client)  # .parsed
            return cls.__new_instance(client.httpx, user)
        except Exception as e:
            raise RuntimeError("Error while retrieving the current user from Argilla.") from e

    @classmethod
    @allowed_for_roles(roles=[UserRole.owner])
    def list(cls) -> Iterator["User"]:
        """Lists all the users in Argilla.

        Returns:
            An iterator of `User` instances.

        Raises:
            RuntimeError: if there was an error while listing the users.

        Examples:
            >>> from argilla_v1 import rg
            >>> for user in rg.User.list():
            ...     print(user)
        """
        client = cls.__active_client()
        try:
            return [cls.__new_instance(client, user) for user in users_api.list_users(client).parsed]
        except Exception as e:
            raise RuntimeError("Error while listing the users from Argilla.") from e
