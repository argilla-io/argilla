#  coding=utf-8
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

from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from fastapi import Depends

from rubrix.server.apis.v0.models.commons.model import TaskType
from rubrix.server.apis.v0.models.datasets import DatasetDB
from rubrix.server.daos.datasets import BaseDatasetDB, DatasetsDAO, SettingsDB
from rubrix.server.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ForbiddenOperationError,
    WrongTaskError,
)
from rubrix.server.security.model import User

Dataset = TypeVar("Dataset", bound=DatasetDB)


class SVCDatasetSettings(SettingsDB):
    pass


class DatasetsService:

    _INSTANCE: "DatasetsService" = None

    @classmethod
    def get_instance(
        cls, dao: DatasetsDAO = Depends(DatasetsDAO.get_instance)
    ) -> "DatasetsService":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetsDAO):
        self.__dao__ = dao

    def create_dataset(
        self, user: User, dataset: Dataset, mappings: Dict[str, Any]
    ) -> Dataset:
        user.check_workspace(dataset.owner)

        try:
            self.find_by_name(
                user=user, name=dataset.name, task=dataset.task, workspace=dataset.owner
            )
            raise EntityAlreadyExistsError(
                name=dataset.name, type=Dataset, workspace=dataset.owner
            )
        except WrongTaskError:  # Found a dataset with same name but different task
            raise EntityAlreadyExistsError(
                name=dataset.name, type=Dataset, workspace=dataset.owner
            )
        except EntityNotFoundError:
            # The dataset does not exist -> create it !
            date_now = datetime.utcnow()
            dataset.created_by = user.username
            dataset.created_at = date_now
            dataset.last_updated = date_now
            return self.__dao__.create_dataset(dataset, mappings=mappings)

    def find_by_name(
        self,
        user: User,
        name: str,
        as_dataset_class: Type[BaseDatasetDB] = DatasetDB,
        task: Optional[TaskType] = None,
        workspace: Optional[str] = None,
    ) -> Dataset:
        owner = user.check_workspace(workspace)

        if task is None:
            found_ds = self.__find_by_name_with_superuser_fallback__(
                user, name=name, owner=owner, as_dataset_class=as_dataset_class
            )
            if found_ds:
                task = found_ds.task

        found_ds = self.__find_by_name_with_superuser_fallback__(
            user, name=name, owner=owner, task=task, as_dataset_class=as_dataset_class
        )

        if found_ds is None:
            raise EntityNotFoundError(name=name, type=Dataset)
        if found_ds.owner and owner and found_ds.owner != owner:
            raise ForbiddenOperationError()

        return cast(Dataset, found_ds)

    def __find_by_name_with_superuser_fallback__(
        self,
        user: User,
        name: str,
        owner: Optional[str],
        as_dataset_class: Optional[Type[DatasetDB]],
        task: Optional[str] = None,
    ):
        found_ds = self.__dao__.find_by_name(
            name=name, owner=owner, task=task, as_dataset_class=as_dataset_class
        )
        if not found_ds and user.is_superuser():
            found_ds = self.__dao__.find_by_name(
                name=name, owner=None, task=task, as_dataset_class=as_dataset_class
            )
        return found_ds

    def delete(self, user: User, dataset: Dataset):
        user.check_workspace(dataset.owner)
        found = self.__find_by_name_with_superuser_fallback__(
            user=user,
            name=dataset.name,
            owner=dataset.owner,
            task=dataset.task,
            as_dataset_class=None,
        )
        if found:
            self.__dao__.delete_dataset(dataset)

    def update(
        self,
        user: User,
        dataset: Dataset,
        tags: Dict[str, str],
        metadata: Dict[str, Any],
    ) -> Dataset:
        found = self.find_by_name(
            user=user, name=dataset.name, task=dataset.task, workspace=dataset.owner
        )

        dataset.tags = {**found.tags, **(tags or {})}
        dataset.metadata = {**found.metadata, **(metadata or {})}
        updated = found.copy(
            update={**dataset.dict(by_alias=True), "last_updated": datetime.utcnow()}
        )
        return self.__dao__.update_dataset(updated)

    def list(
        self,
        user: User,
        workspaces: Optional[List[str]],
        task2dataset_map: Dict[TaskType, Type[BaseDatasetDB]] = None,
    ) -> List[Dataset]:
        owners = user.check_workspaces(workspaces)
        return self.__dao__.list_datasets(
            owner_list=owners, task2dataset_map=task2dataset_map
        )

    def close(self, user: User, dataset: Dataset):
        found = self.find_by_name(user=user, name=dataset.name, workspace=dataset.owner)
        self.__dao__.close(found)

    def open(self, user: User, dataset: Dataset):
        found = self.find_by_name(user=user, name=dataset.name, workspace=dataset.owner)
        self.__dao__.open(found)

    def copy_dataset(
        self,
        user: User,
        dataset: Dataset,
        copy_name: str,
        copy_workspace: Optional[str] = None,
        copy_tags: Dict[str, Any] = None,
        copy_metadata: Dict[str, Any] = None,
    ) -> Dataset:

        dataset_workspace = copy_workspace or dataset.owner
        dataset_workspace = user.check_workspace(dataset_workspace)

        try:
            found = self.find_by_name(
                user=user, name=copy_name, workspace=dataset_workspace
            )
            raise EntityAlreadyExistsError(
                name=found.name, type=found.__class__, workspace=dataset_workspace
            )
        except (EntityNotFoundError, ForbiddenOperationError):
            pass

        copy_dataset = dataset.copy()

        copy_dataset.name = copy_name
        copy_dataset.owner = dataset_workspace

        date_now = datetime.utcnow()
        copy_dataset.created_at = date_now
        copy_dataset.last_updated = date_now

        copy_dataset.tags = {**copy_dataset.tags, **(copy_tags or {})}
        copy_dataset.metadata = {
            **copy_dataset.metadata,
            **(copy_metadata or {}),
            "source_workspace": dataset.owner,
            "copied_from": dataset.name,
        }

        self.__dao__.copy(
            source=dataset,
            target=copy_dataset,
        )

        return copy_dataset

    def all_workspaces(self) -> List[str]:
        """Retrieve all dataset workspaces"""

        workspaces = self.__dao__.get_all_workspaces()
        # include the non-workspace workspace?
        return workspaces

    async def get_settings(
        self, user: User, dataset: Dataset, class_type: Type[SVCDatasetSettings]
    ) -> SVCDatasetSettings:
        """
        Get the configured settings for dataset

        Args:
            user: the connected user
            dataset: the target dataset
            class_type: the settings class

        Returns:
            An instance of class_type settings configured for provided dataset

        """
        settings = self.__dao__.load_settings(dataset=dataset, as_class=class_type)
        if not settings:
            raise EntityNotFoundError(name=dataset.name, type=class_type)
        return class_type.parse_obj(settings.dict())

    async def save_settings(
        self, user: User, dataset: Dataset, settings: SVCDatasetSettings
    ) -> SVCDatasetSettings:
        """
        Save a set of settings for a dataset

        Args:
            user: The user executing the command
            dataset: The dataset
            settings: The dataset settings

        Returns:
            Stored dataset settings

        """
        self.__dao__.save_settings(dataset=dataset, settings=settings)
        return settings

    async def delete_settings(self, user: User, dataset: Dataset) -> None:
        """
        Deletes the dataset settings

        Args:
            user: The user executing the command
            dataset:  The dataset

        """
        self.__dao__.delete_settings(dataset=dataset)
