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

from argilla.server.daos.datasets import BaseDatasetSettingsDB, DatasetsDAO
from argilla.server.daos.models.datasets import BaseDatasetDB
from argilla.server.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ForbiddenOperationError,
    WrongTaskError,
)
from argilla.server.schemas.datasets import CreateDatasetRequest, Dataset
from argilla.server.security.model import User


class ServiceBaseDataset(BaseDatasetDB):
    pass


class ServiceBaseDatasetSettings(BaseDatasetSettingsDB):
    pass


ServiceDataset = TypeVar("ServiceDataset", bound=ServiceBaseDataset)
ServiceDatasetSettings = TypeVar("ServiceDatasetSettings", bound=ServiceBaseDatasetSettings)


class DatasetsService:
    _INSTANCE: "DatasetsService" = None

    @classmethod
    def get_instance(cls, dao: DatasetsDAO = Depends(DatasetsDAO.get_instance)) -> "DatasetsService":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetsDAO):
        self.__dao__ = dao

    def create_dataset(self, user: User, dataset: CreateDatasetRequest) -> BaseDatasetDB:
        dataset.workspace = user.check_workspace(dataset.workspace)
        try:
            self.find_by_name(user=user, name=dataset.name, task=dataset.task, workspace=dataset.workspace)
            raise EntityAlreadyExistsError(name=dataset.name, type=ServiceDataset, workspace=dataset.workspace)
        except WrongTaskError:  # Found a dataset with same name but different task
            raise EntityAlreadyExistsError(name=dataset.name, type=ServiceDataset, workspace=dataset.workspace)
        except EntityNotFoundError:
            # The dataset does not exist -> create it !
            date_now = datetime.utcnow()

            new_dataset = BaseDatasetDB.parse_obj(dataset.dict())
            new_dataset.created_by = user.username
            new_dataset.created_at = date_now
            new_dataset.last_updated = date_now

            return self.__dao__.create_dataset(new_dataset)

    def find_by_name(
        self,
        user: User,
        name: str,
        workspace: str,
        as_dataset_class: Type[ServiceDataset] = ServiceBaseDataset,
        task: Optional[str] = None,
    ) -> ServiceDataset:
        workspace = user.check_workspace(workspace)
        found_ds = self.__dao__.find_by_name(name=name, workspace=workspace, as_dataset_class=as_dataset_class)
        if found_ds is None:
            raise EntityNotFoundError(name=name, type=ServiceDataset)
        elif task and found_ds.task != task:
            raise WrongTaskError(detail=f"Provided task {task} cannot be applied to dataset")
        else:
            return cast(ServiceDataset, found_ds)

    def delete(self, user: User, dataset: ServiceDataset):
        dataset = self.find_by_name(user=user, name=dataset.name, workspace=dataset.workspace, task=dataset.task)

        if user.is_superuser() or user.username == dataset.created_by:
            self.__dao__.delete_dataset(dataset)
        else:
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to delete this dataset. "
                "Only dataset creators or administrators can delete datasets"
            )

    def update(
        self,
        user: User,
        dataset: ServiceDataset,
        tags: Dict[str, str],
        metadata: Dict[str, Any],
    ) -> Dataset:
        found = self.find_by_name(user=user, name=dataset.name, task=dataset.task, workspace=dataset.workspace)

        dataset.tags = {**found.tags, **(tags or {})}
        dataset.metadata = {**found.metadata, **(metadata or {})}
        updated = found.copy(update={**dataset.dict(by_alias=True), "last_updated": datetime.utcnow()})
        return self.__dao__.update_dataset(updated)

    def list(
        self,
        user: User,
        workspaces: Optional[List[str]],
        task2dataset_map: Dict[str, Type[ServiceDataset]] = None,
    ) -> List[ServiceDataset]:
        workspaces = user.check_workspaces(workspaces)
        return self.__dao__.list_datasets(workspaces=workspaces, task2dataset_map=task2dataset_map)

    def close(self, user: User, dataset: ServiceDataset):
        found = self.find_by_name(user=user, name=dataset.name, workspace=dataset.workspace)
        self.__dao__.close(found)

    def open(self, user: User, dataset: ServiceDataset):
        found = self.find_by_name(user=user, name=dataset.name, workspace=dataset.workspace)
        self.__dao__.open(found)

    def copy_dataset(
        self,
        user: User,
        dataset: ServiceDataset,
        copy_name: str,
        copy_workspace: Optional[str] = None,
        copy_tags: Dict[str, Any] = None,
        copy_metadata: Dict[str, Any] = None,
    ) -> ServiceDataset:
        dataset_workspace = copy_workspace or dataset.workspace
        dataset_workspace = user.check_workspace(dataset_workspace)

        self._validate_create_dataset(
            name=copy_name,
            workspace=dataset_workspace,
            user=user,
        )

        copy_dataset = dataset.copy()
        copy_dataset.name = copy_name
        copy_dataset.workspace = dataset_workspace

        date_now = datetime.utcnow()

        copy_dataset.created_at = date_now
        copy_dataset.last_updated = date_now
        copy_dataset.tags = {**copy_dataset.tags, **(copy_tags or {})}
        copy_dataset.metadata = {
            **copy_dataset.metadata,
            **(copy_metadata or {}),
            "source_workspace": dataset.workspace,
            "copied_from": dataset.name,
        }

        self.__dao__.copy(
            source=dataset,
            target=copy_dataset,
        )

        return copy_dataset

    def _validate_create_dataset(self, name: str, workspace: str, user: User):
        try:
            found = self.find_by_name(user=user, name=name, workspace=workspace)
            raise EntityAlreadyExistsError(
                name=found.name,
                type=found.__class__,
                workspace=workspace,
            )
        except (EntityNotFoundError, ForbiddenOperationError):
            pass

    async def get_settings(
        self,
        user: User,
        dataset: ServiceDataset,
        class_type: Type[ServiceDatasetSettings],
    ) -> ServiceDatasetSettings:
        settings = self.__dao__.load_settings(dataset=dataset, as_class=class_type)
        if not settings:
            raise EntityNotFoundError(name=dataset.name, type=class_type)
        return class_type.parse_obj(settings.dict())

    def raw_dataset_update(self, dataset):
        self.__dao__.update_dataset(dataset)

    async def save_settings(
        self, user: User, dataset: ServiceDataset, settings: ServiceDatasetSettings
    ) -> ServiceDatasetSettings:
        self.__dao__.save_settings(dataset=dataset, settings=settings)
        return settings

    async def delete_settings(self, user: User, dataset: ServiceDataset) -> None:
        self.__dao__.delete_settings(dataset=dataset)
