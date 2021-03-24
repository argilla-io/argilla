import ntpath
import os
from glob import glob
from pathlib import Path
from typing import Any, Iterable, List, Optional

import pandas as pd
from rubrix.server.commons.models import TaskType
from rubrix.server.datasets.model import DatasetDB

from .model import CreationDatasetSnapshot, DatasetSnapshotDB
from .settings import settings


class SnapshotsDAO:
    """Abstract class for snapshots data access objects definition"""

    def delete(self, dataset: DatasetDB, id: str) -> None:
        """
        Deletes the given snapshot id

        Parameters
        ----------
        dataset:
            The dataset
        id:str
            The snapshot id


        """
        raise NotImplementedError()

    def create(
        self,
        dataset: DatasetDB,
        task: TaskType,
        snapshot: CreationDatasetSnapshot,
        data: Iterable[Any],
    ) -> DatasetSnapshotDB:
        """
        Creates a snapshot dataset

        Parameters
        ----------
        dataset:
            the dataset
        task: TaskType
            the task related to dataset snapshot
        snapshot:
            the snapshot
        data:
            The snapshot data

        """
        raise NotImplementedError()

    def get(
        self, dataset: DatasetDB, id: str
    ) -> Optional[DatasetSnapshotDB]:
        """

        Parameters
        ----------
        dataset:
            The dataset
        task:
            The task type
        id:str
            The snapshot id

        Returns
        -------

        """
        raise NotImplementedError()

    def list(
        self, dataset: DatasetDB, task: Optional[TaskType] = None
    ) -> List[DatasetSnapshotDB]:
        """
        List dataset snapshots
        Parameters
        ----------
        dataset:
            the dataset
        task:
            The task type. Optional

        Returns
        -------
        A list of dataset snapshots

        """
        raise NotImplementedError()


class LocalSnapshotsDAOImpl(SnapshotsDAO):
    """Snapshots dao implementation based on local folder storage"""

    def __init__(self, folder: str):
        self.__base_path__ = os.path.abspath(folder)

    def create(
        self,
        dataset: DatasetDB,
        task: TaskType,
        snapshot: CreationDatasetSnapshot,
        data: Iterable[Any],
    ) -> DatasetSnapshotDB:
        os.makedirs(
            self.__dataset_snapshots_path__(
                dataset.name, owner=dataset.owner, task=task
            ),
            exist_ok=True,
        )
        path = self.__snapshot_path__(
            dataset.owner, dataset=dataset.name, task=task, id=snapshot.id
        )
        df = pd.DataFrame(data).reset_index()
        if df.empty:
            raise ValueError(
                f"No data for dataset snapshot {dataset.name} and task {task}"
            )
        df.to_json(path, orient="records")
        return DatasetSnapshotDB(id=snapshot.id, uri=path.as_uri())

    def get(
        self, dataset: DatasetDB, id: str
    ) -> Optional[DatasetSnapshotDB]:
        path = self.__snapshot_path__(dataset=dataset.name, owner=dataset.owner, id=id)
        if path:
            return DatasetSnapshotDB(id=id, uri=path.as_uri())

    def list(
        self, dataset: DatasetDB, task: Optional[TaskType] = None
    ) -> List[DatasetSnapshotDB]:
        snapshots_path_pattern = os.path.join(
            self.__dataset_snapshots_path__(
                owner=dataset.owner, dataset=dataset.name, task=task
            ),
            "*",
        )
        return [
            DatasetSnapshotDB(id=ntpath.basename(file), uri=Path(file).as_uri())
            for file in glob(
                snapshots_path_pattern,
                recursive=True,
            )
        ]

    def delete(self, dataset: DatasetDB, id: str) -> None:
        try:
            path = self.__snapshot_path__(dataset.owner, dataset=dataset.name, id=id)
            return os.remove(path)
        except:
            return None

    def __snapshot_path__(
        self, owner: str, dataset: str, id: str, task: Optional[str] = None
    ) -> Optional[Path]:
        snapshots_path = self.__dataset_snapshots_path__(
            dataset, owner=owner, task=task
        )
        if task is None:
            files = glob(os.path.join(snapshots_path, id))
            if len(files) == 0:
                return None
            assert len(files) == 1, f"Corrupted snapshot data for snapshot {id}"
            return Path(files[0])
        return Path(os.path.join(snapshots_path, id))

    def __dataset_snapshots_path__(
        self, dataset: str, owner: str, task: Optional[str] = None
    ) -> Path:
        task = task or "*"
        return Path(os.path.join(self.__owner_snapshots_path__(owner), dataset, task))

    def __owner_snapshots_path__(self, owner: str) -> Path:
        owner = owner or "default"
        return Path(os.path.join(self.__base_path__, owner))


_instance: Optional[SnapshotsDAO] = None


def create_snapshots_dao() -> SnapshotsDAO:
    """
    Creates an snapshots dao instance

    """
    global _instance

    if settings.snapshots_provider == "local":
        if not _instance:
            _instance = LocalSnapshotsDAOImpl(folder=settings.snapshots_path)
        return _instance
