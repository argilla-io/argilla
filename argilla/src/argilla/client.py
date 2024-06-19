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
from typing import TYPE_CHECKING, overload, List, Optional, Union

from argilla import _api
from argilla._api._client import DEFAULT_HTTP_CONFIG
from argilla._helpers import GenericIterator
from argilla._helpers._resource_repr import ResourceHTMLReprMixin
from argilla._models import UserModel, WorkspaceModel, DatasetModel

if TYPE_CHECKING:
    from argilla import Workspace
    from argilla import Dataset
    from argilla import User


__all__ = ["Argilla"]


class Argilla(_api.APIClient):
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
        **http_client_args,
    ) -> None:
        super().__init__(api_url=api_url, api_key=api_key, timeout=timeout, **http_client_args)

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

    @property
    def me(self) -> "User":
        """The current user."""
        from argilla import User

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

    def __call__(self, username: str, **kwargs) -> "User":
        from argilla.users import User

        user_models = self._api.list()
        for model in user_models:
            if model.username == username:
                return User(_model=model, client=self._client)
        warnings.warn(f"User {username} not found. Creating a new user. Do `user.create()` to create the user.")
        return User(username=username, client=self._client, **kwargs)

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
        """Add a new user to the Argilla platform.

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

    def __call__(self, name: str, **kwargs) -> "Workspace":
        from argilla.workspaces import Workspace

        workspace_models = self._api.list()

        for model in workspace_models:
            if model.name == name:
                return Workspace(_model=model, client=self._client)
        warnings.warn(
            f"Workspace {name} not found. Creating a new workspace. Do `workspace.create()` to create the workspace."
        )
        return Workspace(name=name, client=self._client, **kwargs)

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
        return self[0]

    ############################
    # Private methods
    ############################

    def _repr_html_(self) -> str:
        return self._represent_as_html(resources=self.list())

    def _from_model(self, model: WorkspaceModel) -> "Workspace":
        from argilla.workspaces import Workspace

        return Workspace(client=self._client, _model=model)


class Datasets(Sequence["Dataset"], ResourceHTMLReprMixin):
    """A collection of datasets. It can be used to create a new dataset or to get an existing one."""

    class _Iterator(GenericIterator["Dataset"]):
        pass

    def __init__(self, client: "Argilla") -> None:
        self._client = client
        self._api = client.api.datasets

    def __call__(self, name: str, workspace: Optional[Union["Workspace", str]] = None, **kwargs) -> "Dataset":
        from argilla.datasets import Dataset

        if isinstance(workspace, str):
            workspace = self._client.workspaces(workspace)
        elif workspace is None:
            workspace = self._client.workspaces[0]

        for dataset in workspace.datasets:
            if dataset.name == name:
                return dataset
        warnings.warn(f"Dataset {name} not found. Creating a new dataset. Do `dataset.create()` to create the dataset.")
        return Dataset(name=name, workspace=workspace, client=self._client, **kwargs)

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

        return Dataset(client=self._client, _model=model)
