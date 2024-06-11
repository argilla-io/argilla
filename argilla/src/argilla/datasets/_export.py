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

from abc import ABC
import json
import logging
import os
from pathlib import Path
import warnings
from typing import Optional, Union, TYPE_CHECKING, Tuple, Type
from uuid import uuid4

from argilla._models import DatasetModel
from argilla.client import Argilla
from argilla.settings import Settings
from argilla.workspaces._resource import Workspace


if TYPE_CHECKING:
    from argilla import Dataset


class DiskImportExportMixin(ABC):
    """A mixin for exporting and importing datasets to and from disk."""

    _model: DatasetModel
    _default_settings_path = "settings.json"
    _default_records_path = "records.json"
    _default_dataset_path = "dataset.json"

    def to_disk(self: "Dataset", path: str) -> str:
        """Exports the dataset to disk in the given path. The dataset is exported as a directory containing the dataset model, settings and records as json files.

        Args:
            path (str): The path to export the dataset to. Must be an empty directory.
        """
        dataset_path, settings_path, records_path = self._define_child_paths(path=path)
        logging.info(f"Loading dataset from {dataset_path}")
        logging.info(f"Loading settings from {settings_path}")
        logging.info(f"Loading records from {records_path}")
        # Export the dataset model, settings and records
        self._persist_dataset_model(path=dataset_path)
        self.settings.to_json(path=settings_path)
        if self.exists():
            self.records.to_json(path=records_path)
        return path

    @classmethod
    def from_disk(
        cls: Type["Dataset"],
        path: str,
        target_workspace: Optional[Union["Workspace", str]] = None,
        target_name: Optional[str] = None,
        client: Optional["Argilla"] = None,
    ) -> "Dataset":
        """Imports a dataset from disk as a directory containing the dataset model, settings and records.
        The directory should be defined using the `to_disk` method.

        Parameters:
        path (str): The path to the directory containing the dataset model, settings and records.
        target_workspace (Union[Workspace, str], optional): The workspace to import the dataset to. Defaults to None and default workspace is used.
        target_name (str, optional): The name to assign to the new dataset. Defaults to None and the dataset's source name is used, unless it already exists, in which case a unique UUID is appended.
        client (Argilla, optional): The client to use for the import. Defaults to None and the default client is used.
        """

        client = client or Argilla._get_default()

        dataset_path, settings_path, records_path = cls._define_child_paths(path=path)
        logging.info(f"Loading dataset from {dataset_path}")
        logging.info(f"Loading settings from {settings_path}")
        logging.info(f"Loading records from {records_path}")
        dataset_model = cls._load_dataset_model(path=dataset_path)

        # Get the relevant workspace_id of the incoming dataset
        if isinstance(target_workspace, str):
            workspace_id = client.workspaces(target_workspace).id
        elif isinstance(target_workspace, Workspace):
            workspace_id = target_workspace.id
        else:
            warnings.warn("Workspace not provided. Using default workspace.")
            workspace_id = client.workspaces.default.id
        dataset_model.workspace_id = workspace_id

        # Get a relevant and unique name for the incoming dataset.
        if target_name:
            logging.warning(f"Changing dataset name from {dataset_model.name} to {target_name}")
            dataset_model.name = target_name
        elif client.api.datasets.name_exists(name=dataset_model.name, workspace_id=workspace_id):
            logging.warning(f"Loaded dataset name {dataset_model.name} already exists. Changing to unique UUID.")
            dataset_model.name = f"{dataset_model.name}_{uuid4()}"

        # Create the dataset and load the settings and records
        dataset = cls.from_model(model=dataset_model, client=client)
        dataset.settings = Settings.from_json(path=settings_path)
        dataset.create()
        if os.path.exists(records_path):
            dataset.records.from_json(path=records_path)
        return dataset

    ############################
    # Utility methods
    ############################

    def _persist_dataset_model(self, path: Path):
        """Persists the dataset model to disk."""
        if path.exists():
            raise FileExistsError(f"Dataset already exists at {path}")
        with open(file=path, mode="w") as f:
            json.dump(self._model.model_dump(), f)

    @classmethod
    def _load_dataset_model(cls, path: Path):
        """Loads the dataset model from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset model not found at {path}")
        with open(file=path, mode="r") as f:
            dataset_model = json.load(f)
            dataset_model = DatasetModel(**dataset_model)
        return dataset_model

    @classmethod
    def _define_child_paths(cls, path: Union[Path, str]) -> Tuple[Path, Path, Path]:
        path = Path(path)
        if not path.is_dir():
            raise NotADirectoryError(f"Path {path} is not a directory")
        dataset_path = path / cls._default_dataset_path
        settings_path = path / cls._default_settings_path
        records_path = path / cls._default_records_path
        return dataset_path, settings_path, records_path
