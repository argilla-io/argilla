# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings
from abc import abstractmethod
from collections.abc import Sequence
from functools import cached_property
from typing import TYPE_CHECKING, List, Optional, Union, overload
from uuid import UUID

from argilla import _api
from argilla._api._base import ResourceAPI
from argilla._api._client import DEFAULT_HTTP_CONFIG
from argilla._exceptions import ArgillaError, NotFoundError
from argilla._helpers import GenericIterator
from argilla._helpers._deploy import SpacesDeploymentMixin
from argilla._helpers._resource_repr import NotebookHTMLReprMixin, ResourceHTMLReprMixin
from argilla._models import DatasetModel, ResourceModel, UserModel, WorkspaceModel

if TYPE_CHECKING:
    from argilla import Dataset, User, Workspace

__all__ = ["Argilla"]


class Argilla(_api.APIClient, SpacesDeploymentMixin, NotebookHTMLReprMixin):
    """Argilla API client. This is the main entry point to interact with the API.

    Attributes:
        workspaces: A collection of workspaces.
        datasets: A collection of datasets.
        users: A collection of users.
        me: The current user.
    """

    # Default instance of Argilla
    _default_client: Optional["Argilla"] = None

    def __init__(
        self,
        api_url: Optional[str] = DEFAULT_HTTP_CONFIG.api_url,
        api_key: Optional[str] = DEFAULT_HTTP_CONFIG.api_key,
        timeout: int = DEFAULT_HTTP_CONFIG.timeout,
        retries: int = DEFAULT_HTTP_CONFIG.retries,
        **http_client_args,
    ) -> None:
        """Inits the `Argilla` client.

        Args:
            api_url: the URL of the Argilla API. If not provided, then the value will try
                to be set from `ARGILLA_API_URL` environment variable. Defaults to
                `"http://localhost:6900"`.
            api_key: the key to be used to authenticate in the Argilla API. If not provided,
                then the value will try to be set from `ARGILLA_API_KEY` environment variable.
                Defaults to `None`.
            timeout: the maximum time in seconds to wait for a request to the Argilla API
                to be completed before raising an exception. Defaults to `60`.
            retries: the number of times to retry the HTTP connection to the Argilla API
                before raising an exception. Defaults to `5`.
        """
        super().__init__(api_url=api_url, api_key=api_key, timeout=timeout, retries=retries, **http_client_args)

        self._set_default(self)

    @property
    def workspaces(self) -> "Workspaces":
        """A collection of workspaces on the server."""
        return Workspaces(client=self)

    @property
    def datasets(self) -> "Datasets":
        """A collection of datasets on the server."""
        return Datasets(client=self)

    @property
    def users(self) -> "Users":
        """A collection of users on the server."""
        return Users(client=self)

    @cached_property
    def me(self) -> "User":
        from argilla.users import User

        return User(client=self, _model=self.api.users.get_me())

    ############################
    # Private methods
    ############################

    @classmethod
    def _set_default(cls, client: "Argilla") -> None:
        """Set the default instance of Argilla."""
        cls._default_client = client

    @classmethod
    def _get_default(cls) -> "Argilla":
        """Get the default instance of Argilla. If it doesn't exist, create a new one."""
        if cls._default_client is None:
            cls._default_client = Argilla()
        return cls._default_client


class Users(Sequence["User"], ResourceHTMLReprMixin):
    """A collection of users. It can be used to create a new user or to get an existing one."""

    class _Iterator(GenericIterator["User"]):
        pass

    def __init__(self, client: "Argilla") -> None:
        self._client = client
        self._api = client.api.users

    @overload
    def __call__(self, username: str) -> Optional["User"]:
        """Get a user by username if exists. Otherwise, returns `None`"""
        ...

    @overload
    def __call__(self, id: Union[UUID, str]) -> Optional["User"]:
        """Get a user by id if exists. Otherwise, returns `None`"""
        ...

    def __call__(self, username: str = None, id: Union[str, UUID] = None) -> Optional["User"]:
        if not (username or id):
            raise ArgillaError("One of 'username' or 'id' must be provided")
        if username and id:
            warnings.warn("Only one of 'username' or 'id' must be provided. Using 'id'")
            username = None

        if id is not None:
            model = _get_model_by_id(self._api, id)
            if model:
                return self._from_model(model)  # noqa
            warnings.warn(f"User with id {id!r} not found.")
        else:
            for model in self._api.list():
                if model.username == username:
                    return self._from_model(model)
            warnings.warn(f"User with username {username!r} not found.")

    def __iter__(self):
        return self._Iterator(self.list())

    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> "User": ...

    @overload
    @abstractmethod
    def __getitem__(self, index: slice) -> Sequence["User"]: ...

    def __getitem__(self, index):
        model = self._api.list()[index]
        return self._from_model(model)

    def __len__(self) -> int:
        return len(self._api.list())

    def add(self, user: "User") -> "User":
        """Add a new user to Argilla.

        Args:
            user: User object.

        Returns:
            User: The created user.
        """
        user._client = self._client
        return user.create()

    @overload
    def list(self) -> List["User"]: ...

    @overload
    def list(self, workspace: "Workspace") -> List["User"]: ...

    def list(self, workspace: Optional["Workspace"] = None) -> List["User"]:
        """List all users."""
        if workspace is not None:
            models = self._api.list_by_workspace_id(workspace.id)
        else:
            models = self._api.list()

        return [self._from_model(model) for model in models]

    ############################
    # Private methods
    ############################

    def _repr_html_(self) -> str:
        return self._represent_as_html(resources=self.list())

    def _from_model(self, model: UserModel) -> "User":
        from argilla.users import User

        return User(client=self._client, _model=model)


class Workspaces(Sequence["Workspace"], ResourceHTMLReprMixin):
    """A collection of workspaces. It can be used to create a new workspace or to get an existing one."""

    class _Iterator(GenericIterator["Workspace"]):
        pass

    def __init__(self, client: "Argilla") -> None:
        self._client = client
        self._api = client.api.workspaces

    @overload
    def __call__(self, name: str) -> Optional["Workspace"]:
        """Get a workspace by name if exists. Otherwise, returns `None`"""
        ...

    @overload
    def __call__(self, id: Union[UUID, str]) -> Optional["Workspace"]:
        """Get a workspace by id if exists. Otherwise, returns `None`"""
        ...

    def __call__(self, name: str = None, id: Union[UUID, str] = None) -> Optional["Workspace"]:
        if not (name or id):
            raise ArgillaError("One of 'name' or 'id' must be provided")

        if name and id:
            warnings.warn("Only one of 'name' or 'id' must be provided. Using 'id'")
            name = None

        if id is not None:
            model = _get_model_by_id(self._api, id)
            if model:
                return self._from_model(model)  # noqa
            warnings.warn(f"Workspace with id {id!r} not found")
        else:
            for model in self._api.list():
                if model.name == name:
                    return self._from_model(model)  # noqa
            warnings.warn(f"Workspace with name {name!r} not found.")

    def __iter__(self):
        return self._Iterator(self.list())

    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> "Workspace": ...

    @overload
    @abstractmethod
    def __getitem__(self, index: slice) -> Sequence["Workspace"]: ...

    def __getitem__(self, index) -> "Workspace":
        model = self._api.list()[index]
        return self._from_model(model)

    def __len__(self) -> int:
        return len(self._api.list())

    def add(self, workspace: "Workspace") -> "Workspace":
        """Add a new workspace to the Argilla platform.
        Args:
            workspace: Workspace object.

        Returns:
            Workspace: The created workspace.
        """
        workspace._client = self._client
        return workspace.create()

    def list(self) -> List["Workspace"]:
        return [self._from_model(model) for model in self._api.list()]

    ############################
    # Properties
    ############################

    @property
    def default(self) -> "Workspace":
        """The default workspace."""
        if len(self) == 0:
            raise ArgillaError("There are no workspaces created. Please create a new workspace first")
        return self[0]

    ############################
    # Private methods
    ############################

    def _repr_html_(self) -> str:
        return self._represent_as_html(resources=self.list())

    def _from_model(self, model: WorkspaceModel) -> "Workspace":
        from argilla.workspaces import Workspace

        return Workspace.from_model(client=self._client, model=model)


class Datasets(Sequence["Dataset"], ResourceHTMLReprMixin):
    """A collection of datasets. It can be used to create a new dataset or to get an existing one."""

    class _Iterator(GenericIterator["Dataset"]):
        pass

    def __init__(self, client: "Argilla") -> None:
        self._client = client
        self._api = client.api.datasets

    @overload
    def __call__(self, name: str, workspace: Optional[Union["Workspace", str]] = None) -> Optional["Dataset"]:
        """Get a dataset by name and workspace if exists. Otherwise, returns `None`"""
        ...

    @overload
    def __call__(self, id: Union[UUID, str]) -> Optional["Dataset"]:
        """Get a dataset by id if exists. Otherwise, returns `None`"""
        ...

    def __call__(
        self, name: str = None, workspace: Optional[Union["Workspace", str]] = None, id: Union[UUID, str] = None
    ) -> Optional["Dataset"]:
        if not (name or id):
            raise ArgillaError("One of 'name' or 'id' must be provided")

        if name and id:
            warnings.warn("Only one of 'name' or 'id' must be provided. Using 'id'")
            name = None

        if id is not None:
            model = _get_model_by_id(self._api, id)
            if model:
                return self._from_model(model)  # noqa
            warnings.warn(f"Dataset with id {id!r} not found")
        else:
            workspace = workspace or self._client.workspaces.default
            if isinstance(workspace, str):
                workspace = self._client.workspaces(workspace)

            for dataset in workspace.datasets:
                if dataset.name == name:
                    return dataset.get()
            warnings.warn(f"Dataset with name {name!r} not found in workspace {workspace.name!r}")

    def __iter__(self):
        return self._Iterator(self.list())

    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> "Dataset": ...

    @overload
    @abstractmethod
    def __getitem__(self, index: slice) -> Sequence["Dataset"]: ...

    def __getitem__(self, index) -> "Dataset":
        model = self._api.list()[index]
        return self._from_model(model)

    def __len__(self) -> int:
        return len(self._api.list())

    def add(self, dataset: "Dataset") -> "Dataset":
        """
        Add a new dataset to the Argilla platform

        Args:
            dataset: Dataset object.

        Returns:
            Dataset: The created dataset.
        """
        dataset._client = self._client
        dataset.create()

        return dataset

    def list(self) -> List["Dataset"]:
        return [self._from_model(model) for model in self._api.list()]

    ############################
    # Private methods
    ############################

    def _repr_html_(self) -> str:
        return self._represent_as_html(resources=self.list())

    def _from_model(self, model: DatasetModel) -> "Dataset":
        from argilla.datasets import Dataset

        return Dataset.from_model(model=model, client=self._client)


def _get_model_by_id(api: ResourceAPI, resource_id: Union[UUID, str]) -> Optional[ResourceModel]:
    """Get a resource model by id if found. Otherwise, `None`."""
    try:
        if not isinstance(resource_id, UUID):
            resource_id = UUID(resource_id)
        return api.get(resource_id)
    except NotFoundError:
        pass
