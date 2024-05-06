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
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts import accounts
from argilla_server.daos.datasets import BaseDatasetSettingsDB, DatasetsDAO
from argilla_server.daos.models.datasets import BaseDatasetDB
from argilla_server.database import get_async_db
from argilla_server.errors import EntityAlreadyExistsError, EntityNotFoundError, ForbiddenOperationError, WrongTaskError
from argilla_server.models import User, Workspace
from argilla_server.policies import DatasetPolicy, DatasetSettingsPolicy, is_authorized
from argilla_server.schemas.v0.datasets import CreateDatasetRequest, Dataset


class ServiceBaseDataset(BaseDatasetDB):
    pass


ServiceDataset = TypeVar("ServiceDataset", bound=ServiceBaseDataset)
ServiceDatasetSettings = TypeVar("ServiceDatasetSettings", bound=BaseDatasetSettingsDB)


class DatasetsService:
    _INSTANCE: "DatasetsService" = None

    @classmethod
    def get_instance(
        cls, db: AsyncSession = Depends(get_async_db), dao: DatasetsDAO = Depends(DatasetsDAO.get_instance)
    ) -> "DatasetsService":
        return cls(db, dao)

    def __init__(self, db: AsyncSession, dao: DatasetsDAO):
        self._db = db
        self.__dao__ = dao

    async def create_dataset(self, user: User, dataset: CreateDatasetRequest) -> BaseDatasetDB:
        if not await accounts.get_workspace_by_name(self._db, workspace_name=dataset.workspace):
            raise EntityNotFoundError(name=dataset.workspace, type=Workspace)

        if not await is_authorized(user, DatasetPolicy.create(workspace_name=dataset.workspace)):
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to create datasets. Only administrators can create datasets"
            )

        try:
            await self.find_by_name(user=user, name=dataset.name, task=dataset.task, workspace=dataset.workspace)
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

    async def find_by_name(
        self,
        user: User,
        name: str,
        workspace: str,
        as_dataset_class: Type[ServiceDataset] = ServiceBaseDataset,
        task: Optional[Union[str, Enum]] = None,
    ) -> ServiceDataset:
        found_dataset = self.__dao__.find_by_name(name=name, workspace=workspace, as_dataset_class=as_dataset_class)

        if found_dataset is None:
            raise EntityNotFoundError(name=name, type=ServiceDataset)

        elif task and found_dataset.task != task:
            raise WrongTaskError(detail=f"Provided task {task} cannot be applied to dataset")

        if not await is_authorized(user, DatasetPolicy.get(found_dataset)):
            raise ForbiddenOperationError("You don't have the necessary permissions to get this dataset.")

        return cast(ServiceDataset, found_dataset)

    async def delete(self, user: User, dataset: ServiceDataset):
        if not await is_authorized(user, DatasetPolicy.delete(dataset)):
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to delete this dataset. "
                "Only administrators can delete datasets"
            )
        self.__dao__.delete_dataset(dataset)

    async def update(
        self,
        user: User,
        dataset: ServiceDataset,
        tags: Dict[str, str],
        metadata: Dict[str, Any],
    ) -> Dataset:
        found = await self.find_by_name(user=user, name=dataset.name, task=dataset.task, workspace=dataset.workspace)

        if not await is_authorized(user, DatasetPolicy.update(found)):
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to update this dataset. "
                "Only administrators can update datasets"
            )

        dataset.tags = {**found.tags, **(tags or {})}
        dataset.metadata = {**found.metadata, **(metadata or {})}
        updated = found.copy(update={**dataset.dict(by_alias=True), "last_updated": datetime.utcnow()})

        return self.__dao__.update_dataset(updated)

    async def list(
        self,
        user: User,
        workspaces: Optional[List[str]],
        task2dataset_map: Dict[str, Type[ServiceDataset]] = None,
    ) -> List[ServiceDataset]:
        if not await is_authorized(user, DatasetPolicy.list):
            raise ForbiddenOperationError("You don't have the necessary permissions to list datasets.")

        accessible_workspace_names = [
            ws.name for ws in (await accounts.list_workspaces(self._db) if user.is_owner else user.workspaces)
        ]

        if workspaces:
            for ws in workspaces:
                if ws not in accessible_workspace_names:
                    raise EntityNotFoundError(name=ws, type=Workspace)
            workspace_names = workspaces
        else:  # no workspaces
            workspace_names = accessible_workspace_names

        return self.__dao__.list_datasets(workspaces=workspace_names, task2dataset_map=task2dataset_map)

    async def close(self, user: User, dataset: ServiceDataset):
        if not await is_authorized(user, DatasetPolicy.close(dataset)):
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to close this dataset. "
                "Only administrators can close datasets"
            )
        self.__dao__.close(dataset)

    async def open(self, user: User, dataset: ServiceDataset):
        if not await is_authorized(user, DatasetPolicy.open(dataset)):
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to open this dataset. "
                "Only administrators can open datasets"
            )
        self.__dao__.open(dataset)

    async def copy_dataset(
        self,
        user: User,
        dataset: ServiceDataset,
        copy_name: str,
        copy_workspace: Optional[str] = None,
        copy_tags: Dict[str, Any] = None,
        copy_metadata: Dict[str, Any] = None,
    ) -> ServiceDataset:
        target_workspace_name = copy_workspace or dataset.workspace

        target_workspace = await accounts.get_workspace_by_name(self._db, target_workspace_name)
        if not target_workspace:
            raise EntityNotFoundError(name=target_workspace_name, type=Workspace)

        if self.__dao__.find_by_name_and_workspace(name=copy_name, workspace=target_workspace_name):
            raise EntityAlreadyExistsError(name=copy_name, workspace=target_workspace_name, type=Dataset)

        if not await is_authorized(user, DatasetPolicy.copy(dataset, target_workspace=target_workspace)):
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to copy this dataset. "
                "Only administrators can copy datasets"
            )

        dataset_copy = dataset.copy()
        dataset_copy.name = copy_name
        dataset_copy.workspace = target_workspace_name
        dataset_copy.created_by = user.username

        date_now = datetime.utcnow()

        dataset_copy.created_at = date_now
        dataset_copy.last_updated = date_now
        dataset_copy.tags = {**dataset_copy.tags, **(copy_tags or {})}
        dataset_copy.metadata = {
            **dataset_copy.metadata,
            **(copy_metadata or {}),
            "source_workspace": dataset.workspace,
            "copied_from": dataset.name,
        }

        self.__dao__.copy(source=dataset, target=dataset_copy)

        return dataset_copy

    async def get_settings(
        self,
        user: User,
        dataset: ServiceDataset,
        class_type: Type[ServiceDatasetSettings],
    ) -> ServiceDatasetSettings:
        settings = self.__dao__.load_settings(dataset=dataset, as_class=class_type)
        if not settings:
            raise EntityNotFoundError(name=dataset.name, type=class_type)

        if not await is_authorized(user, DatasetSettingsPolicy.list(dataset)):
            raise ForbiddenOperationError("You don't have the necessary permissions to list settings for this dataset.")
        return class_type.parse_obj(settings.dict())

    def raw_dataset_update(self, dataset):
        self.__dao__.update_dataset(dataset)

    async def save_settings(
        self, user: User, dataset: ServiceDataset, settings: ServiceDatasetSettings
    ) -> ServiceDatasetSettings:
        if not await is_authorized(user, DatasetSettingsPolicy.save(dataset)):
            raise ForbiddenOperationError("You don't have the necessary permissions to save settings for this dataset.")

        self.__dao__.save_settings(dataset=dataset, settings=settings)
        return settings

    async def delete_settings(self, user: User, dataset: ServiceDataset) -> None:
        if not await is_authorized(user, DatasetSettingsPolicy.delete(dataset)):
            raise ForbiddenOperationError(
                "You don't have the necessary permissions to delete settings for this dataset."
            )

        self.__dao__.delete_settings(dataset=dataset)
