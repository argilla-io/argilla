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
from typing import List, Optional

from fastapi import Depends

from rubrix.server.commons.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ForbiddenOperationError,
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
from ..metrics.model import DatasetMetric, DatasetMetricDB


class DatasetsService:
    """Datasets service"""

    def __init__(self, dao: DatasetsDAO):
        self.__dao__ = dao

    def list(
        self, owners: List[str] = None, task_type: Optional[TaskType] = None
    ) -> List[Dataset]:
        """
        List datasets for a list of owners and task types

        Parameters
        ----------
        owners:
            The owners list. Optional
        task_type:
            The task type: Optional

        Returns
        -------
            A list of datasets
        """
        return [
            Dataset(**obs.dict())
            for obs in self.__dao__.list_datasets(owner_list=owners)
            if task_type is None or task_type == obs.task
        ]

    def create(
        self,
        dataset: CreationDatasetRequest,
        owner: Optional[str],
        task: TaskType,
    ) -> Dataset:
        """
        Creates a datasets from given creation request

        Parameters
        ----------
        dataset:
            The dataset creation fields
        owner:
            The dataset owner. Optional
        task:
            The dataset task

        Returns
        -------
            The created dataset

        """
        date_now = datetime.utcnow()
        db_dataset = DatasetDB(
            **dataset.dict(by_alias=True),
            task=task,
            owner=owner,
            created_at=date_now,
            last_updated=date_now
        )
        created_dataset = self.__dao__.create_dataset(db_dataset)
        return Dataset.parse_obj(created_dataset)

    def find_by_name(self, name: str, owner: Optional[str]) -> DatasetDB:
        """
        Find a dataset by name

        Parameters
        ----------
        name:
            The dataset name
        owner:
            The dataset owner. Optional

        Returns
        -------
            - The found dataset
            - EntityNotFoundError if not found
            - ForbiddenOperationError if user cannot access the dataset

        """
        found = self.__dao__.find_by_name(name, owner=owner)
        if not found:
            raise EntityNotFoundError(name=name, type=Dataset)
        if found.owner and owner and found.owner != owner:
            raise ForbiddenOperationError()
        return found

    def delete(self, name: str, owner: Optional[str]):
        """
        Deletes a dataset.

        Parameters
        ----------
        name:
            The dataset name
        owner:
            The dataset owner

        """
        found = self.__dao__.find_by_name(name, owner)
        if found:
            self.__dao__.delete_dataset(found)

    def update(
        self,
        name: str,
        owner: Optional[str],
        data: UpdateDatasetRequest,
    ) -> Dataset:
        """
        Updates an existing dataset. Fields in update data are
        merged with store ones. Updates cannot remove data fields.

        Parameters
        ----------
        name:
            The dataset name
        owner:
            The dataset owner
        data:
            The update fields

        Returns
        -------
            The updated dataset
        """

        found = self.find_by_name(name, owner)

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
        owner: Optional[str],
        task: Optional[TaskType] = None,
    ) -> Dataset:
        """
        Inserts or updates the dataset. Updates only affects to updatable fields

        Parameters
        ----------
        dataset:
            The dataset data
        owner:
            The dataset owner
        task:
            The dataset task type

        Returns
        -------

            The updated or created dataset

        """
        try:
            return self.update(
                name=dataset.name,
                owner=owner,
                data=UpdateDatasetRequest(tags=dataset.tags, metadata=dataset.metadata),
            )
        except EntityNotFoundError:
            return self.create(
                dataset=dataset,
                task=task or TaskType.text_classification,
                owner=owner,
            )

    def copy_dataset(
        self, name: str, owner: Optional[str], data: CopyDatasetRequest
    ) -> Dataset:
        try:
            self.find_by_name(data.name, owner=owner)
            raise EntityAlreadyExistsError(name=data.name, type=Dataset)
        except (EntityNotFoundError, ForbiddenOperationError):
            pass
        found = self.find_by_name(name, owner)
        date_now = datetime.utcnow()
        created_dataset = DatasetDB(
            name=data.name,
            task=found.task,
            owner=owner,
            created_at=date_now,
            last_updated=date_now,
            tags={**found.tags, **data.tags},
            metadata={**found.metadata, **data.metadata, "copied_from": found.name},
        )
        self.__dao__.copy(
            source=found,
            target=created_dataset,
        )

        return Dataset.parse_obj(created_dataset)

    def close_dataset(self, name: str, owner: Optional[str]):
        found = self.find_by_name(name, owner)
        self.__dao__.close(found)

    def open_dataset(self, name: str, owner: Optional[str]):
        found = self.find_by_name(name, owner)
        self.__dao__.open(found)

    def get_dataset_metrics(
        self, name: str, owner: Optional[str]
    ) -> List[DatasetMetricDB]:
        found = self.find_by_name(name, owner)
        return found.metrics

    def add_dataset_metric(
        self, name: str, owner: Optional[str], metric: DatasetMetricDB
    ) -> DatasetMetricDB:
        found = self.find_by_name(name, owner)
        for ds_metric in found.metrics:
            if ds_metric.name == metric.name:
                raise EntityAlreadyExistsError(metric.name, DatasetMetric)
        if not metric.spec:
            metric.spec = self.__dao__.generate_dataset_metric_spec(found, metric)
        found.metrics.append(metric)
        self.__dao__.update_dataset(found)
        return metric

    def delete_dataset_metric(
        self, name: str, owner: Optional[str], metric_id: str
    ) -> None:
        found = self.find_by_name(name, owner)
        if metric_id not in [m.id for m in found.metrics]:
            raise EntityNotFoundError(metric_id, DatasetMetric)
        found.metrics = [m for m in found.metrics if m.id != metric_id]
        self.__dao__.update_dataset(found)


_instance: Optional[DatasetsService] = None


def create_dataset_service(
    dao: DatasetsDAO = Depends(create_datasets_dao),
) -> DatasetsService:
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

    global _instance

    if not _instance:
        _instance = DatasetsService(dao)
    return _instance
