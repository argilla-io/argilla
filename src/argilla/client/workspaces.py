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
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from argilla.client import active_client

if TYPE_CHECKING:
    from argilla.client.sdk.workspaces.models import WorkspaceUserModel

from datetime import datetime

from argilla.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    BaseClientError,
    NotFoundApiError,
    ValidationApiError,
)
from argilla.client.sdk.v1.workspaces import api as workspaces_api_v1
from argilla.client.sdk.workspaces import api as workspaces_api


class Workspace:
    """The `Workspace` class is used to manage workspaces in Argilla. It provides
    methods to create new workspaces, adding users to them, listing the linked users,
    and deleting users from the workspace. While it's not allowed to delete a workspace
    neither to update the workspace name.

    Args:
        name: the name of the workspace to be managed. Defaults to None.
        id: the ID of the workspace to be managed. Defaults to None.

    Attributes:
        id: the ID of the workspace.
        name: the name of the workspace.
        users: the list of users linked to the workspace. Defaults to None.
        inserted_at: the datetime when the workspace was created.
        updated_at: the datetime when the workspace was last updated.

    Raises:
        ValueError: if the workspace does not exist in the current Argilla account,
            if both `name` and `id` are provided, or if none of them is provided, or
            if the provided `id` is not a valid UUID.
        RuntimeError: if there was an error while retrieving the workspace/s from Argilla.

    Examples:
        >>> from argilla import rg
        >>> workspace = rg.Workspace("my-workspace")
        >>> workspace.add_user("my-user")
        >>> print(workspace.users)
        [WorkspaceUserModel(id='...', first_name='Luke', last_name="Skywalker', full_name='Luke Skywalker', username='my-user', role='annotator', workspaces=['my-workspace'], api_key='...', inserted_at=datetime.datetime(2021, 8, 31, 10, 0, 0), updated_at=datetime.datetime(2021, 8, 31, 10, 0, 0))]
        >>> workspace.delete_user("my-user")
        >>> print(workspace.users)
        []
    """

    id: UUID
    name: str
    users: Optional[List["WorkspaceUserModel"]] = None
    inserted_at: datetime
    updated_at: datetime

    def __init__(self, name: Optional[str] = None, *, id: Optional[str] = None) -> None:
        """Initializes a `Workspace` instance. It can be initialized either by providing
        the workspace name or the workspace ID, but in any case, the workspace must exist
        in the current Argilla account in advance.

        Args:
            name: the name of the workspace to be managed. Defaults to None.
            id: the ID of the workspace to be managed. Defaults to None.

        Raises:
            ValueError: if the workspace does not exist in the current Argilla account.
            ValidationApiError: if the ID provided is not a valid UUID.
            RuntimeError: if there was an error while retrieving the workspace/s from Argilla.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace("my-workspace")
            >>> workspace = rg.Workspace(id="...")
        """
        if name is None and id is None:
            raise ValueError("At least one of `name` or `id` must be provided.")
        if name is not None and id is not None:
            raise ValueError("Just one of `name` or `id` must be provided.")

        existing_workspace = None
        if id is not None:
            try:
                existing_workspace = workspaces_api_v1.get_workspace(active_client().http_client.httpx, id).parsed
            except NotFoundApiError as e:
                raise ValueError(
                    f"Workspace with id=`{id}` doesn't exist in Argilla, so please"
                    " make sure that the ID you provided is a valid one. Otherwise,"
                    " you can create a new one via the `Workspace.create` method."
                ) from e
            except ValidationApiError as e:
                raise ValueError(
                    "The ID you provided is not a valid UUID, so please make sure"
                    " that the ID you provided is a valid one."
                ) from e
            except BaseClientError as e:
                raise RuntimeError(f"Error while retrieving workspace with id=`{id}` from Argilla.") from e
        elif name is not None:
            try:
                workspaces = workspaces_api.list_workspaces(active_client().http_client.httpx).parsed
            except Exception as e:
                raise RuntimeError("Error while retrieving the list of workspaces from Argilla.") from e
            for workspace in workspaces:
                if workspace.name == name:
                    existing_workspace = workspace
                    break

            if existing_workspace is None:
                raise ValueError(
                    f"Workspace with name=`{name}` doesn't exist in Argilla, so please"
                    "create it via the `Workspace.create` method as follows:"
                    f" `Workspace(name=`{name}`)`."
                )
        self.__dict__.update(existing_workspace.dict())

    @property
    def users(self) -> List["WorkspaceUserModel"]:
        """Returns the list of users linked to the workspace.

        Returns:
            A list of `WorkspaceUserModel` instances.
        """
        if not hasattr(self, "__users") or self.__users is None:
            self.__users = workspaces_api.list_workspace_users(active_client().http_client.httpx, self.id).parsed
        return self.__users

    def __str__(self) -> str:
        return f"Workspace(id={self.id}, name={self.name}, users={self.users}, insterted_at={self.inserted_at}, updated_at={self.updated_at}"

    def add_user(self, id: str) -> None:
        """Adds an existing user to the workspace in Argilla.

        Args:
            id: the ID of the user to be added to the workspace. The user must exist in Argilla.

        Raises:
            ValueError: if the user with the provided ID already exists in the workspace.
            RuntimeError: if there was an error while adding the user to the workspace.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace("my-workspace")
            >>> workspace.add_user("my-user")
        """
        try:
            created_user = workspaces_api.create_workspace_user(
                client=active_client().http_client.httpx,
                id=self.id,
                user_id=id,
            )
        except AlreadyExistsApiError as e:
            raise ValueError(f"User with id=`{id}` already exists in workspace with id=`{self.id}`.") from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while adding user with id=`{id}` to workspace with id=`{self.id}`.") from e

        if len(self.users) == 0:
            self.__users = [created_user]
        else:
            self.__users.append(created_user)

    def delete_user(self, id: str) -> None:
        """Deletes an existing user from the workspace in Argilla. Note that the user
        will not be deleted from Argilla, but just from the workspace.

        Args:
            id: the ID of the user to be deleted from the workspace. The user must exist in Argilla.

        Raises:
            ValueError: if the user with the provided ID doesn't exist in the workspace.
            RuntimeError: if there was an error while deleting the user from the workspace.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace("my-workspace")
            >>> workspace.delete_user("my-user")
        """
        try:
            workspaces_api.delete_workspace_user(
                client=active_client().http_client.httpx,
                id=self.id,
                user_id=id,
            )
        except NotFoundApiError as e:
            raise ValueError(
                f"Either the user with id=`{id}` doesn't exist in Argilla, or it doesn't belong to workspace with id=`{self.id}`."
            ) from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while deleting user with id=`{id}` from workspace with id=`{self.id}`.") from e

        self.__users = [user for user in self.users if user.id != id]

    @classmethod
    def create(cls, name: str) -> "Workspace":
        """Creates a new workspace in Argilla.

        Args:
            name: the name of the workspace to be created.

        Raises:
            ValueError: if the workspace with the provided name already exists.

        Returns:
            A `Workspace` instance.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace.create("my-workspace")
        """
        try:
            workspace = workspaces_api.create_workspace(
                client=active_client().http_client.httpx,
                name=name,
            ).parsed
        except AlreadyExistsApiError as e:
            raise ValueError(f"Workspace with name=`{name}` already exists, so please use a different name.") from e
        except (ValidationApiError, BaseClientError) as e:
            raise RuntimeError(f"Error while creating workspace with name=`{name}`.") from e

        instance = cls.__new__(cls)
        instance.__dict__.update(workspace.dict())
        return instance

    @classmethod
    def from_name(cls, name: str) -> "Workspace":
        """Deprecated! Use `Workspace(name)` instead."""
        warnings.warn(
            "The `Workspace.from_name` method is deprecated and will be removed in"
            " the 1.11.0 release of Argilla. Please use `Workspace(name)` instead.",
            DeprecationWarning,
        )
        return Workspace(name=name)
