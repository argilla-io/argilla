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

from argilla.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    BaseClientError,
    NotFoundApiError,
    ValidationApiError,
)
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.workspaces import api as workspaces_api_v1
from argilla.client.sdk.v1.workspaces.models import WorkspaceModel as WorkspaceModelV1
from argilla.client.sdk.workspaces import api as workspaces_api
from argilla.client.sdk.workspaces.models import WorkspaceModel as WorkspaceModelV0
from argilla.client.singleton import active_client
from argilla.client.users import User
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    import httpx

    from argilla.client.sdk.users.models import UserModel


class Workspace:
    """The `Workspace` class is used to manage workspaces in Argilla. It provides
    methods to create new workspaces, add users to them, list the linked users,
    and delete users from the workspace. While it's not allowed to delete a workspace
    neither to update the workspace name.

    Args:
        name: the name of the workspace to be managed. Defaults to None.
        id: the ID of the workspace to be managed. Defaults to None.

    Attributes:
        _client: the `httpx.Client` initialized to interact with the Argilla API.
        id: the ID of the workspace.
        name: the name of the workspace.
        users: the list of users linked to the workspace. Defaults to None.
        inserted_at: the datetime when the workspace was created.
        updated_at: the datetime when the workspace was last updated.

    Examples:
        >>> from argilla import rg
        >>> workspace = rg.Workspace.from_name("my-workspace") # or `Workspace.from_id("...")`
        >>> workspace.add_user("my-user")
        >>> print(workspace.users)
        [UserModel(id='...', first_name='Luke', last_name="Skywalker', full_name='Luke Skywalker', username='my-user', role='annotator', workspaces=['my-workspace'], api_key='...', inserted_at=datetime.datetime(2021, 8, 31, 10, 0, 0), updated_at=datetime.datetime(2021, 8, 31, 10, 0, 0))]
        >>> workspace.delete_user("my-user")
        >>> print(workspace.users)
        []
    """

    _client: "httpx.Client"  # Required to be able to use `allowed_for_roles` decorator
    id: UUID
    name: str
    users: Optional[List["UserModel"]] = None
    inserted_at: datetime
    updated_at: datetime

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        id: Optional[Union[str, UUID]] = None,
    ) -> None:
        """Doesn't initialize the `Workspace`, as it needs to be instantiated via any of
        the following classmethods, as the Argilla API is required.
            - `Workspace.create` to create a new workspace in Argilla
            - `Workspace.from_name` to get an existing workspace from Argilla by its name
            - `Workspace.from_id` to get an existing workspace from Argilla by its ID
            - `Workspace.list` to list all the workspaces in Argilla

        Args:
            name: the name of the workspace to be managed. Defaults to None.
            id: the ID of the workspace to be managed. Defaults to None.

        Raises:
            Exception: if the `Workspace` is initialized via the `__init__` method.
        """
        error_msg = (
            "`Workspace` cannot be initialized via the `__init__` method, as it needs"
            " to send requests to the Argilla API, so it can just be instantiated via"
            " the following classmethods: `Workspace.create`, `Workspace.from_name`,"
            " `Workspace.from_id` and `Workspace.list`; note that it must exist in"
            " advance in Argilla."
        )
        if id is not None:
            error_msg += f" As the `id` argument is not None, you should use `Workspace.from_id('{id}')` instead."
        if name is not None:
            error_msg += f" As the `name` argument is not None, you should use `Workspace.from_name('{name}')` instead."
        raise Exception(error_msg)

    @property
    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def users(self) -> List["UserModel"]:
        """Returns the list of users linked to the workspace.

        Returns:
            A list of `UserModel` instances.
        """
        # TODO(@alvarobartt): Maybe we should return a list of rg.User instead.
        return workspaces_api.list_workspace_users(self._client, self.id).parsed

    def __repr__(self) -> str:
        return (
            f"Workspace(id={self.id}, name={self.name},"
            f" inserted_at={self.inserted_at}, updated_at={self.updated_at})"
        )

    @allowed_for_roles(roles=[UserRole.owner])
    def add_user(self, user_id: UUID) -> None:
        """Adds an existing user to the workspace in Argilla.

        Note that users with the `owner` role are excluded from the `add_user` method, as they
        are superusers and they can access all the workspaces and datasets in Argilla.

        Args:
            user_id: the ID of the user to be added to the workspace. The user must exist in Argilla.

        Raises:
            ValueError: if the user with the provided ID either doesn't exist in Argilla or
                already exists in the workspace.
            RuntimeError: if there was an error while either fetching the user from Argilla or
                adding the user to the workspace.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace.from_name("my-workspace")
            >>> workspace.add_user("my-user-id")
        """
        try:
            user = User.from_id(user_id)
        except ValueError as e:
            raise ValueError(
                f"User with id=`{user_id}` doesn't exist in Argilla, so please"
                " make sure that the ID you provided is a valid one. Otherwise,"
                " you can create a new one via the `User.create` method."
            ) from e
        except RuntimeError as e:
            raise RuntimeError(f"Error while retrieving user with id=`{user_id}` from Argilla.") from e

        if user.is_owner:
            warnings.warn(
                "The user you are trying to add to the workspace has the `owner` role, so it"
                " will be excluded from the workspace. Note that users with the `owner` role are"
                " superusers and they can access all the workspaces and datasets in Argilla.",
                UserWarning,
                stacklevel=2,
            )
            return

        try:
            workspaces_api.create_workspace_user(client=self._client, id=self.id, user_id=user_id)
        except AlreadyExistsApiError as e:
            raise ValueError(f"User with id=`{user_id}` already exists in workspace with id=`{self.id}`.") from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while adding user with id=`{user_id}` to workspace with id=`{self.id}`.") from e

    @allowed_for_roles(roles=[UserRole.owner])
    def delete_user(self, user_id: UUID) -> None:
        """Deletes an existing user from the workspace in Argilla. Note that the user
        will not be deleted from Argilla, but just from the workspace.

        Note that users with the `owner` role are excluded from the `delete_user` method, as they
        are superusers and they can access all the workspaces and datasets in Argilla.

        Args:
            user_id: the ID of the user to be deleted from the workspace. The user must exist in Argilla.

        Raises:
            ValueError: if the user with the provided ID doesn't exist in either the workspace or Argilla.
            RuntimeError: if there was an error while retrieving the user from Argilla or
                while deleting it from the workspace.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace.from_name("my-workspace")
            >>> workspace.delete_user("my-user-id")
        """
        try:
            user = User.from_id(user_id)
        except ValueError as e:
            raise ValueError(
                f"User with id=`{user_id}` doesn't exist in Argilla, so please"
                " make sure that the ID you provided is a valid one. Otherwise,"
                " you can create a new one via the `User.create` method."
            ) from e
        except RuntimeError as e:
            raise RuntimeError(f"Error while retrieving user with id=`{user_id}` from Argilla.") from e

        if user.is_owner:
            warnings.warn(
                "The user you are trying to delete from the workspace has the `owner` role, so it"
                " will be excluded from the workspace. Note that users with the `owner` role are"
                " superusers and they can access all the workspaces and datasets in Argilla.",
                UserWarning,
                stacklevel=2,
            )
            return

        try:
            workspaces_api.delete_workspace_user(client=self._client, id=self.id, user_id=user_id)
        except NotFoundApiError as e:
            raise ValueError(
                f"Either the user with id=`{user_id}` doesn't exist in Argilla, or it"
                f" doesn't belong to workspace with id=`{self.id}`."
            ) from e
        except BaseClientError as e:
            raise RuntimeError(
                f"Error while deleting user with id=`{user_id}` from workspace with id=`{self.id}`."
            ) from e

    @allowed_for_roles(roles=[UserRole.owner])
    def delete(self) -> None:
        """Deletes an existing workspace from Argilla. Note that the workspace
        cannot have any linked dataset to be removed from Argilla. Otherwise, an error will be raised.

        Raises:
            ValueError: if the workspace does not exist or some datasets are linked to it.
            RuntimeError: if there was an unexpected error while deleting the user from the workspace.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace.from_name("my-workspace")
            >>> workspace.delete()
        """
        try:
            workspaces_api_v1.delete_workspace(client=self._client, id=self.id)
        except NotFoundApiError as e:
            raise ValueError(f"Workspace with id {self.id} doesn't exist in Argilla.") from e
        except AlreadyExistsApiError as e:
            # TODO: the already exists is to explicit for this context and should be generalized
            raise ValueError(
                f"Cannot delete workspace with id {self.id}. Some datasets are still linked to this workspace."
            ) from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while deleting workspace with id {self.id!r}.") from e

    @staticmethod
    def __active_client() -> "httpx.Client":
        """Returns the active Argilla `httpx.Client` instance."""
        try:
            return active_client().http_client.httpx
        except Exception as e:
            raise RuntimeError(f"The `rg.active_client()` is not available or not responding.") from e

    @classmethod
    def _new_instance(
        cls, client: Optional["httpx.Client"] = None, ws: Optional[Union[WorkspaceModelV0, WorkspaceModelV1]] = None
    ) -> "Workspace":
        """Returns a new `Workspace` instance."""
        instance = cls.__new__(cls)
        instance._client = client or cls.__active_client()
        if isinstance(ws, (WorkspaceModelV0, WorkspaceModelV1)):
            instance.__dict__.update(ws.dict())
        return instance

    @classmethod
    @allowed_for_roles(roles=[UserRole.owner])
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
        client = cls.__active_client()
        try:
            ws = workspaces_api.create_workspace(client, name).parsed
            return cls._new_instance(client, ws)
        except AlreadyExistsApiError as e:
            raise ValueError(f"Workspace with name=`{name}` already exists, so please use a different name.") from e
        except (ValidationApiError, BaseClientError) as e:
            raise RuntimeError(f"Error while creating workspace with name=`{name}`.") from e

    @classmethod
    def from_id(cls, id: UUID) -> "Workspace":
        """Gets an existing workspace from Argilla by its ID.

        Args:
            id: the ID of the workspace to be retrieved.

        Returns:
            A `Workspace` instance.

        Raises:
            ValueError: if the workspace with the provided ID doesn't exist, or if it's
                not a valid UUID identifier.
            RuntimeError: if there was an error while retrieving the workspace.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace.from_id("my-workspace-id")
        """
        client = cls.__active_client()
        try:
            ws = workspaces_api_v1.get_workspace(client, id).parsed
            return cls._new_instance(client, ws)
        except NotFoundApiError as e:
            raise ValueError(
                f"Workspace with id=`{id}` doesn't exist in Argilla, so please"
                " make sure that the ID you provided is a valid one. Otherwise,"
                " you can create a new one via the `Workspace.create` method."
            ) from e
        except ValidationApiError as e:
            raise ValueError(
                "The ID you provided is not a valid UUID, so please make sure that the"
                " ID you provided is a valid one."
            ) from e
        except BaseClientError as e:
            raise RuntimeError(f"Error while retrieving workspace with id=`{id}` from Argilla.") from e

    @classmethod
    def from_name(cls, name: str) -> "Workspace":
        """Gets an existing workspace from Argilla by its name.

        Args:
            name: the name of the workspace to be retrieved.

        Returns:
            A `Workspace` instance.

        Raises:
            RuntimeError: if there was an error while listing the workspaces.
            ValueError: if the workspace with the provided name doesn't exist.

        Examples:
            >>> from argilla import rg
            >>> workspace = rg.Workspace.from_name("my-workspace")
        """
        client = cls.__active_client()
        try:
            workspaces = workspaces_api_v1.list_workspaces_me(client).parsed
        except Exception as e:
            raise RuntimeError("Error while retrieving the list of workspaces from Argilla.") from e

        for ws in workspaces:
            if ws.name == name:
                return cls._new_instance(client, ws)

        raise ValueError(
            f"Workspace with name=`{name}` doesn't exist in Argilla, so please"
            " create it via the `Workspace.create` method as follows:"
            f" `Workspace.create('{name}')`."
        )

    @classmethod
    def list(cls) -> Iterator["Workspace"]:
        """Lists all the workspaces in Argilla.

        Returns:
            A list of `Workspace` instances.

        Raises:
            RuntimeError: if there was an error while listing the workspaces.

        Examples:
            >>> from argilla import rg
            >>> workspaces = rg.Workspace.list()
        """
        client = cls.__active_client()
        try:
            return [
                cls._new_instance(client, workspace)
                for workspace in workspaces_api_v1.list_workspaces_me(client).parsed
            ]

        except Exception as e:
            raise RuntimeError("Error while retrieving the list of workspaces from Argilla.") from e
