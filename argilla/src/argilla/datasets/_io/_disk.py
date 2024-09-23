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

import json
import logging
import os
import warnings
from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple, Type, Union

from argilla._exceptions import RecordsIngestionError, ArgillaError, ImportDatasetError
from argilla._models import DatasetModel
from argilla.client import Argilla
from argilla.settings import Settings
from argilla.workspaces._resource import Workspace

if TYPE_CHECKING:
    from argilla import Dataset


class DiskImportExportMixin(ABC):
    """A mixin for exporting and importing datasets to and from disk."""

    _model: DatasetModel
    _DEFAULT_RECORDS_PATH = "records.json"
    _DEFAULT_CONFIG_REPO_DIR = ".argilla"
    _DEFAULT_SETTINGS_PATH = f"{_DEFAULT_CONFIG_REPO_DIR}/settings.json"
    _DEFAULT_DATASET_PATH = f"{_DEFAULT_CONFIG_REPO_DIR}/dataset.json"
    _DEFAULT_CONFIGURATION_FILES = [_DEFAULT_SETTINGS_PATH, _DEFAULT_DATASET_PATH]

    def to_disk(self: "Dataset", path: str, *, with_records: bool = True) -> str:
        """Exports the dataset to disk in the given path. The dataset is exported as a directory containing the dataset model, settings and records as json files.

        Parameters:
            path (str): The path to export the dataset to. Must be an empty directory.
            with_records: whether to load the records from the Hugging Face dataset. Defaults to `True`.
        """
        dataset_path, settings_path, records_path = self._define_child_paths(path=path)
        logging.info(f"Loading dataset from {dataset_path}")
        logging.info(f"Loading settings from {settings_path}")
        logging.info(f"Loading records from {records_path}")
        # Export the dataset model, settings and records
        self._persist_dataset_model(path=dataset_path)
        self.settings.to_json(path=settings_path)
        if with_records:
            self.records.to_json(path=records_path)

        return path

    @classmethod
    def from_disk(
        cls: Type["Dataset"],
        path: str,
        *,
        name: Optional[str] = None,
        workspace: Optional[Union["Workspace", str]] = None,
        client: Optional["Argilla"] = None,
        with_records: bool = True,
    ) -> "Dataset":
        """Imports a dataset from disk as a directory containing the dataset model, settings and records.
        The directory should be defined using the `to_disk` method.

        Parameters:
            path (str): The path to the directory containing the dataset model, settings and records.
            name (str, optional): The name to assign to the new dataset. Defaults to None and the dataset's source name is used, unless it already exists, in which case a unique UUID is appended.
            workspace (Union[Workspace, str], optional): The workspace to import the dataset to. Defaults to None and default workspace is used.
            client (Argilla, optional): The client to use for the import. Defaults to None and the default client is used.
            with_records: whether to load the records from the Hugging Face dataset. Defaults to `True`.
        """

        client = client or Argilla._get_default()

        try:
            dataset_path, settings_path, records_path = cls._define_child_paths(path=path)
            logging.info(f"Loading dataset from {dataset_path}")
            logging.info(f"Loading settings from {settings_path}")
            logging.info(f"Loading records from {records_path}")

            dataset_model = cls._load_dataset_model(path=dataset_path)
        except (NotADirectoryError, FileNotFoundError) as e:
            raise ImportDatasetError(f"Error loading dataset from disk. {e}") from e

        # Get the relevant workspace_id of the incoming dataset
        if isinstance(workspace, str):
            workspace = client.workspaces(workspace)
            if not workspace:
                raise ArgillaError(f"Workspace {workspace} not found on the server.")
        else:
            warnings.warn("Workspace not provided. Using default workspace.")
            workspace = client.workspaces.default
        dataset_model.workspace_id = workspace.id

        if name and (name != dataset_model.name):
            logging.info(f"Changing dataset name from {dataset_model.name} to {name}")
            dataset_model.name = name

        if client.api.datasets.name_exists(name=dataset_model.name, workspace_id=workspace.id):
            warnings.warn(
                f"Loaded dataset name {dataset_model.name} already exists in the workspace {workspace.name} so using it. To create a new dataset, provide a unique name to the `name` parameter."
            )
            dataset_model = client.api.datasets.get_by_name_and_workspace_id(
                name=dataset_model.name, workspace_id=workspace.id
            )
            dataset = cls.from_model(model=dataset_model, client=client)
        else:
            # Create a new dataset and load the settings and records
            if not os.path.exists(settings_path):
                raise ImportDatasetError(f"Settings file not found at {settings_path}")

            dataset = cls.from_model(model=dataset_model, client=client)
            dataset.settings = Settings.from_json(path=settings_path)
            dataset.create()

        if os.path.exists(records_path) and with_records:
            try:
                dataset.records.from_json(path=records_path)
            except RecordsIngestionError as e:
                raise RecordsIngestionError(
                    message="Error importing dataset records from disk. "
                    "Records and datasets settings are not compatible."
                ) from e

        return dataset

    ############################
    # Utility methods
    ############################

    def _persist_dataset_model(self, path: Path):
        """Persists the dataset model to disk."""
        if path.exists():
            raise FileExistsError(f"Dataset already exists at {path}")
        with open(file=path, mode="w") as f:
            json.dump(self.api_model().model_dump(), f)

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
        main_path = path / cls._DEFAULT_CONFIG_REPO_DIR
        main_path.mkdir(exist_ok=True)
        dataset_path = path / cls._DEFAULT_DATASET_PATH
        settings_path = path / cls._DEFAULT_SETTINGS_PATH
        records_path = path / cls._DEFAULT_RECORDS_PATH
        return dataset_path, settings_path, records_path
