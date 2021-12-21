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
from typing import ClassVar, List, Optional

from fastapi import Depends

from rubrix.server.commons.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ForbiddenOperationError,
    WrongTaskError,
)
from .dao import DatasetsDAO, create_datasets_dao
from .model import (
    CopyDatasetRequest,
    CreationDatasetRequest,
    Dataset,
    DatasetDB,
    TaskType,
    UpdateDatasetRequest,
)
from ..security.model import User


class DatasetsService:
    """Datasets service"""

    _INSTANCE: ClassVar["DatasetsService"] = None

    @classmethod
    def get_instance(
        cls, dao: DatasetsDAO = Depends(create_datasets_dao)
    ) -> "DatasetsService":

        """
        Creates an instance of service

        Parameters
        ----------
        dao:
            The datasets dao

        Returns
        -------
            An instance of dataset service

        """

        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetsDAO):
        self.__dao__ = dao

    def list(
        self, user: User, workspaces: List[str], task_type: Optional[TaskType] = None
    ) -> List[Dataset]:
        """
        List datasets for a list of owners and task types

        Parameters
        ----------
        user:
            The request user
        workspaces:
            A list of selected user teams
        task_type:
            The task type: Optional

        Returns
        -------
            A list of datasets
        """
        owners = user.check_workspaces(workspaces)

        return [
            Dataset(**obs.dict())
            for obs in self.__dao__.list_datasets(owner_list=owners)
            if task_type is None or task_type == obs.task
        ]

    def create(
        self,
        dataset: CreationDatasetRequest,
        task: TaskType,
        user: User,
        workspace: Optional[str],
    ) -> Dataset:
        """
        Creates a datasets from given creation request

        Parameters
        ----------
        dataset:
            The dataset creation fields
        task:
            The dataset task
        user:
            The current user
        workspace:
            The user workspace selected for dataset creation

        Returns
        -------
            The created dataset

        """
        owner = user.check_workspace(workspace)
        date_now = datetime.utcnow()
        db_dataset = DatasetDB(
            **dataset.dict(by_alias=True),
            task=task,
            owner=owner,
            created_at=date_now,
            last_updated=date_now,
        )
        created_dataset = self.__dao__.create_dataset(db_dataset)
        return Dataset.parse_obj(created_dataset)

    def find_by_name(
        self, name: str, task: Optional[TaskType], user: User, workspace: Optional[str]
    ) -> DatasetDB:
        """
        Find a dataset by name

        Parameters
        ----------
        name:
            The dataset name
        task:
            Related dataset task
        user:
            The current user
        workspace:
            The user workspace where dataset belongs to

        Returns
        -------
            - The found dataset
            - EntityNotFoundError if not found
            - ForbiddenOperationError if user cannot access the dataset

        """
        owner = user.check_workspace(workspace)
        found = self.__dao__.find_by_name(name, owner=owner)
        if not found:
            raise EntityNotFoundError(name=name, type=Dataset)
        if found.owner and owner and found.owner != owner:
            raise ForbiddenOperationError()
        if task and found.task != task:
            raise WrongTaskError(f"Provided task {task} cannot be applied to dataset")
        return found

    def delete(self, name: str, user: User, workspace: Optional[str]):
        """
        Deletes a dataset.

        Parameters
        ----------
        name:
            The dataset name
        user:
            The current user
        workspace:
            The team where dataset belongs to

        """
        owner = user.check_workspace(workspace)
        found = self.__dao__.find_by_name(name, owner)
        if found:
            self.__dao__.delete_dataset(found)

    def update(
        self,
        name: str,
        data: UpdateDatasetRequest,
        user: User,
        workspace: Optional[str],
    ) -> Dataset:
        """
        Updates an existing dataset. Fields in update data are
        merged with store ones. Updates cannot remove data fields.

        Parameters
        ----------
        name:
            The dataset name
        data:
            The update fields
        user:
            The current user
        workspace:
            The workspace where dataset belongs to

        Returns
        -------
            The updated dataset
        """

        found = self.find_by_name(name, task=None, user=user, workspace=workspace)

        data.tags = {**found.tags, **data.tags}
        data.metadata = {**found.metadata, **data.metadata}
        updated = found.copy(
            update={**data.dict(by_alias=True), "last_updated": datetime.utcnow()}
        )

        self.__dao__.update_dataset(updated)
        return Dataset(**updated.dict(by_alias=True))

    def upsert(
        self,
        dataset: CreationDatasetRequest,
        task: TaskType,
        user: User,
        workspace: Optional[str],
    ) -> Dataset:
        """
        Inserts or updates the dataset. Updates only affects to updatable fields

        Parameters
        ----------
        dataset:
            The dataset data
        task:
            Selected task when dataset does not exists. Won't be used
            if dataset already exists
        user:
            The current user
        workspace:
            The dataset where dataset belongs to

        Returns
        -------

            The updated or created dataset

        """
        try:
            return self.update(
                name=dataset.name,
                data=UpdateDatasetRequest(tags=dataset.tags, metadata=dataset.metadata),
                user=user,
                workspace=workspace,
            )
        except EntityNotFoundError:
            return self.create(
                dataset=dataset, task=task, user=user, workspace=workspace
            )

    def copy_dataset(
        self,
        name: str,
        data: CopyDatasetRequest,
        user: User,
        workspace: Optional[str],
    ) -> Dataset:
        """
        Copies a dataset into another

        Parameters
        ----------
        name:
            The source dataset name
        data:
            A copy request configuration
        user:
            The current user
        workspace:
            The workspace where source dataset belongs to

        Returns
        -------

        """
        dataset_workspace = data.target_workspace or workspace
        dataset_workspace = user.check_workspace(dataset_workspace)

        try:
            self.find_by_name(data.name, task=None, user=user, workspace=dataset_workspace)
            raise EntityAlreadyExistsError(name=data.name, type=Dataset, workspace=dataset_workspace)
        except (EntityNotFoundError, ForbiddenOperationError):
            pass

        found = self.find_by_name(name, task=None, user=user, workspace=workspace)
        date_now = datetime.utcnow()

        created_dataset = DatasetDB(
            name=data.name,
            task=found.task,
            owner=dataset_workspace,
            created_at=date_now,
            last_updated=date_now,
            tags={**found.tags, **data.tags},
            metadata={
                **found.metadata,
                **data.metadata,
                "source_workspace": workspace,
                "copied_from": found.name,
            },
        )
        self.__dao__.copy(
            source=found,
            target=created_dataset,
        )

        return Dataset.parse_obj(created_dataset)

    def close_dataset(self, name: str, user: User, workspace: Optional[str]):
        """
        Closes a dataset. That means that all related dataset resources
        will be releases, but dataset cannot be explored

        Parameters
        ----------
        name:
            The dataset name
        user:
            The current user
        workspace:
            The workspace where dataset belongs to

        """
        found = self.find_by_name(name, task=None, user=user, workspace=workspace)
        self.__dao__.close(found)

    def open_dataset(self, name: str, user: User, workspace: Optional[str]):
        """
        Open a dataset. That means that all related dataset resources
        will be loaded and dataset will be ready for searches

        Parameters
        ----------
        name:
            The dataset name
        user:
            The current user
        workspace:
            The workspace where dataset belongs to

        """
        found = self.find_by_name(name, task=None, user=user, workspace=workspace)
        self.__dao__.open(found)
