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

from argilla._api import DatasetsAPI
from argilla._exceptions import NotFoundError, SettingsError
from argilla._helpers import UUIDUtilities
from argilla._models import DatasetModel
from argilla._resource import Resource
from argilla.client import Argilla
from argilla.datasets._export import DiskImportExportMixin
from argilla.records import DatasetRecords
from argilla.settings import Settings
from argilla.workspaces._resource import Workspace

__all__ = ["Dataset"]


class Dataset(Resource, DiskImportExportMixin):
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
        workspace: Optional[Union["Workspace", str]] = None,
        settings: Optional[Settings] = None,
        client: Optional["Argilla"] = None,
        _model: Optional[DatasetModel] = None,
    ) -> None:
        """Initializes a new Argilla Dataset object with the given parameters.

        Parameters:
            name (str): Name of the dataset. Replaced by random UUID if not assigned.
            workspace (UUID): Workspace of the dataset. Default is the first workspace found in the server.
            settings (Settings): Settings class to be used to configure the dataset.
            client (Argilla): Instance of Argilla to connect with the server. Default is the default client.
            _model (DatasetModel): Model of the dataset. Used to create the dataset from an existing model.
        """
        client = client or Argilla._get_default()
        super().__init__(client=client, api=client.api.datasets)
        if name is None:
            name = f"dataset_{uuid4()}"
            self._log_message(f"Settings dataset name to unique UUID: {name}")

        self.workspace_id = (
            _model.workspace_id if _model and _model.workspace_id else self._workspace_id_from_name(workspace=workspace)
        )
        self._model = _model or DatasetModel(
            name=name,
            workspace_id=UUIDUtilities.convert_optional_uuid(uuid=self.workspace_id),
        )
        self._settings = settings or Settings(_dataset=self)
        self._settings.dataset = self
        self.__records = DatasetRecords(client=self._client, dataset=self)

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
        if self._is_published() and self._settings.is_outdated:
            self._settings.get()
        return self._settings

    @settings.setter
    def settings(self, value: Settings) -> None:
        value.dataset = self
        self._settings = value

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

    #####################
    #  Core methods     #
    #####################

    def exists(self) -> bool:
        """Checks if the dataset exists on the server

        Returns:
            bool: True if the dataset exists, False otherwise
        """
        return self.id and self._api.exists(self.id)

    def create(self) -> "Dataset":
        """Creates the dataset on the server with the `Settings` configuration.

        Returns:
            Dataset: The created dataset object.
        """
        super().create()
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

    @classmethod
    def from_model(cls, model: DatasetModel, client: "Argilla") -> "Dataset":
        return cls(client=client, _model=model)

    #####################
    #  Utility methods  #
    #####################

    def _publish(self) -> "Dataset":
        self._settings.create()
        self._api.publish(dataset_id=self._model.id)

        return self.get()  # type: ignore

    def _workspace_id_from_name(self, workspace: Optional[Union["Workspace", str]]) -> UUID:
        if workspace is None:
            available_workspaces = self._client.workspaces
            ws = available_workspaces[0]  # type: ignore
            warnings.warn(f"Workspace not provided. Using default workspace: {ws.name} id: {ws.id}")
        elif isinstance(workspace, str):
            available_workspace_names = [ws.name for ws in self._client.workspaces]
            ws = self._client.workspaces(workspace)
            if not ws.exists():
                self._log_message(
                    message=f"Workspace with name {workspace} not found. \
                        Available workspaces: {available_workspace_names}",
                    level="error",
                )
                raise NotFoundError()
        else:
            ws = workspace
        return ws.id

    def _rollback_dataset_creation(self):
        if self.exists() and not self._is_published():
            self.delete()

    def _is_published(self) -> bool:
        return self.exists() and self._model.status == "ready"
