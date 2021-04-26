from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends
from rubrix.server.commons.errors import EntityNotFoundError
from rubrix.server.datasets.service import DatasetsService, create_dataset_service
from rubrix.server.tasks.commons import TaskStatus, TaskType
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.tasks.commons.es_helpers import filters

from .dao import SnapshotsDAO, create_snapshots_dao
from .model import CreationDatasetSnapshot, DatasetSnapshot


class SnapshotsService:
    """
    The snapshots service
    """

    def __init__(
        self,
        dao: SnapshotsDAO,
        datasets: DatasetsService,
        dataset_records: DatasetRecordsDAO,
    ):
        self.__dao__ = dao
        self.__datasets__ = datasets
        self.__dataset_records__ = dataset_records

    def get(self, dataset: str, owner: Optional[str], id: str) -> DatasetSnapshot:
        """
        Get a dataset snapshot by id

        Parameters
        ----------
        dataset:
            Dataset name
        owner:
            Dataset owner. Optional
        id:
            Snapshot id

        Returns
        -------

        """
        dataset = self.__datasets__.find_by_name(name=dataset, owner=owner)
        found = self.__dao__.get(dataset, id=id)
        if found is None:
            raise EntityNotFoundError(id, DatasetSnapshot)
        return DatasetSnapshot.parse_obj(found)

    def list(
        self, dataset: str, owner: Optional[str], task: Optional[TaskType] = None
    ) -> List[DatasetSnapshot]:
        """
        List the dataset snapshots

        Parameters
        ----------
        dataset:
            Dataset name
        owner:
            Dataset owner
        task:
            Task type records selector

        Returns
        -------
            Snapshots list
        """
        dataset = self.__datasets__.find_by_name(name=dataset, owner=owner)
        return [
            DatasetSnapshot.parse_obj(snap)
            for snap in self.__dao__.list(dataset=dataset, task=task)
        ]

    def create(self, dataset: str, owner: Optional[str]) -> DatasetSnapshot:
        """
        Creates a dataset snapshot

        Parameters
        ----------
        dataset:
            Dataset name
        owner:
            Dataset owner. Optional

        Returns
        -------
            Created dataset snapshot info

        """
        dataset = self.__datasets__.find_by_name(name=dataset, owner=owner)
        task = dataset.task
        task_records = self.__dataset_records__.scan_dataset(
            dataset=dataset,
            search=RecordSearch(query=filters.status(status=[TaskStatus.validated])),
        )

        created = self.__dao__.create(
            dataset=dataset,
            task=task,
            snapshot=CreationDatasetSnapshot(id=str(datetime.utcnow().timestamp())),
            data=(self.record_to_snapshot(record, task) for record in task_records),
        )

        return DatasetSnapshot.parse_obj(created)

    def delete(
        self,
        dataset: str,
        owner: Optional[str],
        id: str,
    ):
        """
        Deletes an snapshot by id

        Parameters
        ----------
        dataset:
            Dataset name
        owner:
            Dataset owner. Optional
        id:
            Snapshot id

        """
        dataset = self.__datasets__.find_by_name(name=dataset, owner=owner)
        return self.__dao__.delete(dataset=dataset, id=id)

    @staticmethod
    def record_to_snapshot(record: Dict[str, Any], task: TaskType) -> Dict[str, Any]:
        """Convert a record dict into an snapshot data structure"""
        # TODO: task level logic should be place in each task module and this method should coordinate
        #  depending on incoming task argument
        metadata = record.get("metadata", {})
        data = {"id": record["id"], **{k: v for k, v in metadata.items()}}
        if task == TaskType.text_classification:
            multi_label = record.get("multi_label", False)
            data.update(
                {
                    "labels": record["annotated_as"]
                    if multi_label
                    else record["annotated_as"][0],
                    **{k: v for k, v in record["inputs"].items()},
                }
            )
        elif task == TaskType.token_classification:
            data.update(
                {
                    "tokens": record["tokens"],
                    "text": record["raw_text"],
                    "entities": record["annotation"]["entities"],
                }
            )
        return data


_instance: Optional[DatasetsService] = None


def create_snapshots_service(
    dao: SnapshotsDAO = Depends(create_snapshots_dao),
    datasets: DatasetsService = Depends(create_dataset_service),
    dataset_records: DatasetRecordsDAO = Depends(dataset_records_dao),
) -> SnapshotsService:
    """
    Creates the dataset snapshots service

    Parameters
    ----------
    dao:
        Snapshots dao dependency
    datasets:
        Datasets service dependency
    dataset_records:
        Dataset records dependency

    """
    global _instance
    if not _instance:
        _instance = SnapshotsService(
            dao=dao, datasets=datasets, dataset_records=dataset_records
        )
    return _instance
