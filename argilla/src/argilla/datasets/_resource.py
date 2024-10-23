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
from typing import Optional, Union
from uuid import UUID, uuid4

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from argilla._api import DatasetsAPI
from argilla._exceptions import NotFoundError, SettingsError, ForbiddenError
from argilla._models import DatasetModel
from argilla._resource import Resource
from argilla.client import Argilla
from argilla.datasets._io import DiskImportExportMixin, HubImportExportMixin
from argilla.records import DatasetRecords
from argilla.settings import Settings
from argilla.settings._task_distribution import TaskDistribution
from argilla.workspaces._resource import Workspace

__all__ = ["Dataset"]


class Dataset(Resource, HubImportExportMixin, DiskImportExportMixin):
    """Class for interacting with Argilla Datasets

    Attributes:
        name: Name of the dataset.
        records (DatasetRecords): The records object for the dataset. Used to interact with the records of the dataset by iterating, searching, etc.
        settings (Settings): The settings object of the dataset. Used to configure the dataset with fields, questions, guidelines, etc.
        fields (list): The fields of the dataset, for example the `rg.TextField` of the dataset. Defined in the settings.
        questions (list): The questions of the dataset defined in the settings. For example, the `rg.TextQuestion` that you want labelers to answer.
        guidelines (str): The guidelines of the dataset defined in the settings. Used to provide instructions to labelers.
        allow_extra_metadata (bool): True if extra metadata is allowed, False otherwise.
    """

    name: str
    id: Optional[UUID]

    _api: "DatasetsAPI"
    _model: "DatasetModel"

    def __init__(
        self,
        name: Optional[str] = None,
        workspace: Optional[Union["Workspace", str, UUID]] = None,
        settings: Optional[Settings] = None,
        client: Optional["Argilla"] = None,
    ) -> None:
        """Initializes a new Argilla Dataset object with the given parameters.

        Parameters:
            name (str): Name of the dataset. Replaced by random UUID if not assigned.
            workspace (UUID): Workspace of the dataset. Default is the first workspace found in the server.
            settings (Settings): Settings class to be used to configure the dataset.
            client (Argilla): Instance of Argilla to connect with the server. Default is the default client.
        """
        client = client or Argilla._get_default()
        super().__init__(client=client, api=client.api.datasets)
        if name is None:
            name = f"dataset_{uuid4()}"
            self._log_message(f"Settings dataset name to unique UUID: {name}")

        self._workspace = workspace
        self._model = DatasetModel(name=name)
        self._settings = settings._copy() if settings else Settings(_dataset=self)
        self._settings.dataset = self
        self.__records = DatasetRecords(client=self._client, dataset=self, mapping=self._settings.mapping)

    #####################
    #  Properties       #
    #####################

    @property
    def name(self) -> str:
        return self._model.name

    @name.setter
    def name(self, value: str) -> None:
        self._model.name = value

    @property
    def records(self) -> "DatasetRecords":
        return self.__records

    @property
    def settings(self) -> Settings:
        return self._settings

    @settings.setter
    def settings(self, value: Settings) -> None:
        settings_copy = value._copy()
        settings_copy.dataset = self
        self._settings = settings_copy

    @property
    def fields(self) -> list:
        return self.settings.fields

    @property
    def questions(self) -> list:
        return self.settings.questions

    @property
    def guidelines(self) -> str:
        return self.settings.guidelines

    @guidelines.setter
    def guidelines(self, value: str) -> None:
        self.settings.guidelines = value

    @property
    def allow_extra_metadata(self) -> bool:
        return self.settings.allow_extra_metadata

    @allow_extra_metadata.setter
    def allow_extra_metadata(self, value: bool) -> None:
        self.settings.allow_extra_metadata = value

    @property
    def schema(self) -> dict:
        return self.settings.schema

    @property
    def workspace(self) -> Workspace:
        self._workspace = self._resolve_workspace()
        return self._workspace

    @property
    def distribution(self) -> TaskDistribution:
        return self.settings.distribution

    @distribution.setter
    def distribution(self, value: TaskDistribution) -> None:
        self.settings.distribution = value

    #####################
    #  Core methods     #
    #####################

    def get(self) -> "Dataset":
        super().get()
        self.settings.get()
        return self

    def create(self) -> "Dataset":
        """Creates the dataset on the server with the `Settings` configuration.

        Returns:
            Dataset: The created dataset object.
        """
        try:
            super().create()
        except ForbiddenError as e:
            settings_url = f"{self._client.api_url}/user-settings"
            user_role = self._client.me.role.value
            user_name = self._client.me.username
            workspace_name = self.workspace.name
            message = f"""User '{user_name}' is not authorized to create a dataset in workspace '{workspace_name}'
            with role '{user_role}'. Go to {settings_url} to view your role."""
            raise ForbiddenError(message) from e
        try:
            return self._publish()
        except Exception as e:
            self._log_message(message=f"Error creating dataset: {e}", level="error")
            self._rollback_dataset_creation()
            raise SettingsError from e

    def update(self) -> "Dataset":
        """Updates the dataset on the server with the current settings.

        Returns:
            Dataset: The updated dataset object.
        """
        self.settings.update()
        return self

    def progress(self, with_users_distribution: bool = False) -> dict:
        """Returns the team's progress on the dataset.

        Parameters:
            with_users_distribution (bool): If True, the progress of the dataset is returned
                with users distribution. This includes the number of responses made by each user.

        Returns:
            dict: The team's progress on the dataset.

        An example of a response when `with_users_distribution` is `True`:
        ```json
        {
            "total": 100,
            "completed": 50,
            "pending": 50,
            "users": {
                "user1": {
                   "completed": { "submitted": 10, "draft": 5, "discarded": 5},
                   "pending": { "submitted": 5, "draft": 10, "discarded": 10},
                },
                "user2": {
                   "completed": { "submitted": 20, "draft": 10, "discarded": 5},
                   "pending": { "submitted": 2, "draft": 25, "discarded": 0},
                },
                ...
        }
        ```

        """

        progress = self._api.get_progress(dataset_id=self._model.id).model_dump()

        if with_users_distribution:
            users_progress = self._api.list_users_progress(dataset_id=self._model.id)
            users_distribution = {
                user.username: {
                    "completed": user.completed.model_dump(),
                    "pending": user.pending.model_dump(),
                }
                for user in users_progress
            }

            progress.update({"users": users_distribution})

        return progress

    @classmethod
    def from_model(cls, model: DatasetModel, client: "Argilla") -> "Dataset":
        instance = cls(client=client, workspace=model.workspace_id, name=model.name)
        instance._model = model

        return instance

    #####################
    #  Utility methods  #
    #####################

    def api_model(self) -> DatasetModel:
        self._model.workspace_id = self.workspace.id
        return self._model

    def _publish(self) -> "Dataset":
        self._settings.create()
        self._api.publish(dataset_id=self._model.id)

        return self.get()

    def _resolve_workspace(self) -> Workspace:
        workspace = self._workspace

        if workspace is None:
            workspace = self._client.workspaces.default
            warnings.warn(f"Workspace not provided. Using default workspace: {workspace.name} id: {workspace.id}")
        elif isinstance(workspace, str):
            workspace = self._client.workspaces(workspace)
            if workspace is None:
                available_workspace_names = [ws.name for ws in self._client.workspaces]
                raise NotFoundError(
                    f"Workspace with name {workspace} not found. Available workspaces: {available_workspace_names}"
                )
        elif isinstance(workspace, UUID):
            ws_model = self._client.api.workspaces.get(workspace)
            workspace = Workspace.from_model(ws_model, client=self._client)
        elif not isinstance(workspace, Workspace):
            raise ValueError(f"Wrong workspace value found {workspace}")

        return workspace

    def _rollback_dataset_creation(self):
        if not self._is_published():
            self.delete()

    def _is_published(self) -> bool:
        return self._model.status == "ready"

    def _with_client(self, client: Argilla) -> "Self":
        return super()._with_client(client=client)

    @classmethod
    def _run_settings_ui(cls, repo_id: str, subset: str, split: str, client: Optional["Argilla"] = None) -> str:
        from urllib.parse import quote_plus, urlencode
        import webbrowser

        client = client or Argilla._get_default()

        params = {
            "subset": subset,
            "split": split,
        }

        url = f"{client.api_url}/new/{quote_plus(repo_id)}?{urlencode(params)}"

        try:
            webbrowser.open(url, new=2, autoraise=True)
        except Exception as e:
            warnings.warn(f"Error opening the URL in the browser: {e}")
        finally:
            warnings.warn(f"Open the following URL in your browser to configure the dataset: {url}")
            return url
