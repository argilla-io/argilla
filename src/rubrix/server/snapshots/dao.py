import datetime
import ntpath
import os
from glob import glob
from pathlib import Path
from typing import Any, Iterable, List, Optional

import pandas as pd
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.tasks.commons import TaskType

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

    def get(self, dataset: DatasetDB, id: str) -> Optional[DatasetSnapshotDB]:
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
            _dataset_snapshots_path(
                base_path=self.__base_path__,
                dataset=dataset.name,
                owner=dataset.owner,
                task=task,
            ),
            exist_ok=True,
        )
        paths = _snapshot_path_matches(
            base_path=self.__base_path__,
            dataset=dataset.name,
            owner=dataset.owner,
            task=task,
            id=snapshot.id,
        )
        assert len(paths) == 1, f"Corrupted snapshot data for snapshot {id}"

        path = paths[0]
        df = pd.DataFrame(data).reset_index()
        if df.empty:
            raise ValueError(
                f"No data for dataset snapshot {dataset.name} and task {task}"
            )
        df.to_json(path, orient="records", lines=True)
        return DatasetSnapshotDB(
            id=snapshot.id,
            uri=path.as_uri(),
            task=_task_from_path(str(path)),
            creation_date=self.__file_creation_date__(path),
        )

    def get(self, dataset: DatasetDB, id: str) -> Optional[DatasetSnapshotDB]:
        paths = _snapshot_path_matches(
            base_path=self.__base_path__,
            dataset=dataset.name,
            owner=dataset.owner,
            id=id,
        )
        if paths:
            path = paths[0]
            return DatasetSnapshotDB(
                id=id,
                uri=path.as_uri(),
                task=_task_from_path(str(path)),
                creation_date=self.__file_creation_date__(path),
            )

    def list(
        self, dataset: DatasetDB, task: Optional[TaskType] = None
    ) -> List[DatasetSnapshotDB]:
        paths = _snapshot_path_matches(
            base_path=self.__base_path__,
            owner=dataset.owner,
            dataset=dataset.name,
            task=task,
            id="*",
        )
        return [
            DatasetSnapshotDB(
                id=ntpath.basename(file),
                uri=file.as_uri(),
                task=_task_from_path(str(file)),
                creation_date=self.__file_creation_date__(file),
            )
            for file in paths
        ]

    def delete(self, dataset: DatasetDB, id: str) -> None:
        try:
            paths = _snapshot_path_matches(
                base_path=self.__base_path__,
                dataset=dataset.name,
                owner=dataset.owner,
                id=id,
            )
            for path in paths:
                return os.remove(path)
        except:
            return None

    @staticmethod
    def __file_creation_date__(path: Path) -> datetime.datetime:
        stats = path.stat()
        return datetime.datetime.fromtimestamp(stats.st_ctime)


def _owner_snapshots_path(base_path: str, owner: Optional[str]) -> Path:
    """
    Composes snapshots owner's path from a given base path

    Parameters
    ----------
    base_path:
        The base path
    owner
        The owner
    """
    owner = owner or "default"
    return Path(os.path.join(base_path, owner))


def _dataset_snapshots_path(
    base_path: str, dataset: str, owner: Optional[str], task: Optional[str] = None
) -> Path:
    """
    Composes snapshots dataset's path

    Parameters
    ----------
    base_path:
        Base path
    dataset:
        The dataset name
    owner:
        The dataset's owner
    task
        The snapshot task
    """
    task = task or "**"
    return Path(os.path.join(_owner_snapshots_path(base_path, owner), dataset, task))


def _task_from_path(file: str) -> str:
    """
    Calculates the snapshot task from a given file path

    Parameters
    ----------
    file:
        The file path
    """
    snapshot_id, task, *_ = list(reversed(file.split(os.sep)))
    return task


def _snapshot_path_matches(
    base_path: str,
    owner: str,
    dataset: str,
    id: str,
    task: Optional[str] = None,
    glob_fn=glob,
) -> List[Path]:
    """Return path matches for snapshot path pattern"""
    snapshots_path = _dataset_snapshots_path(
        base_path=base_path, dataset=dataset, owner=owner, task=task
    )
    path_pattern = os.path.join(snapshots_path, id)
    if task is None:
        files = glob_fn(path_pattern)
        return list(map(Path, files))
    return [Path(path_pattern)]


class S3SnapshotsDAOImpl(SnapshotsDAO):
    """Snapshots backend using s3 storage"""

    def __init__(self, bucket_name: str):
        import s3fs

        self.__s3__ = s3fs.S3FileSystem()
        assert self.__s3__.exists(bucket_name), (
            f"Provided bucket '{bucket_name}' does not exist or aws credentials was not properly configured. "
            "See <https://boto3.amazonaws.com/v1/documentation"
            "/api/latest/guide/configuration.html#using-environment-variables>"
        )
        self.__bucket__ = bucket_name

    def delete(self, dataset: DatasetDB, id: str) -> None:
        paths = _snapshot_path_matches(
            base_path=self.__bucket__,
            owner=dataset.owner,
            dataset=dataset.name,
            id=id,
            glob_fn=self.__s3__.glob,
        )
        for path in paths:
            self.__s3__.rm(str(path))

    def create(
        self,
        dataset: DatasetDB,
        task: TaskType,
        snapshot: CreationDatasetSnapshot,
        data: Iterable[Any],
    ) -> DatasetSnapshotDB:
        path = _snapshot_path_matches(
            self.__bucket__,
            owner=dataset.owner,
            dataset=dataset.name,
            task=task,
            id=snapshot.id,
            glob_fn=self.__s3__.glob,
        )[0]

        df = pd.DataFrame(data).reset_index()
        if df.empty:
            raise ValueError(
                f"No data for dataset snapshot {dataset.name} and task {task}"
            )
        s3_uri = f"s3://{path}"
        df.to_json(s3_uri, orient="records", lines=True)

        return DatasetSnapshotDB(
            id=snapshot.id,
            uri=s3_uri,
            task=_task_from_path(s3_uri),
            creation_date=self.__date_from_s3_path(str(path)),
        )

    def get(self, dataset: DatasetDB, id: str) -> Optional[DatasetSnapshotDB]:
        paths = _snapshot_path_matches(
            base_path=self.__bucket__,
            dataset=dataset.name,
            owner=dataset.owner,
            id=id,
            glob_fn=self.__s3__.glob,
        )
        if paths:
            path = str(paths[0])
            return DatasetSnapshotDB(
                id=id,
                uri=f"s3://{path}",
                task=_task_from_path(str(path)),
                creation_date=self.__date_from_s3_path(path),
            )

    def list(
        self, dataset: DatasetDB, task: Optional[TaskType] = None
    ) -> List[DatasetSnapshotDB]:
        files = _snapshot_path_matches(
            base_path=self.__bucket__,
            dataset=dataset.name,
            owner=dataset.owner,
            id="*",
            glob_fn=self.__s3__.glob,
        )
        return [
            DatasetSnapshotDB(
                id=ntpath.basename(file),
                uri=f"s3://{file}",
                task=_task_from_path(str(file)),
                creation_date=self.__date_from_s3_path(str(file)),
            )
            for file in files
        ]

    def __date_from_s3_path(self, path: str) -> datetime.datetime:
        return self.__s3__.stat(path)[
            "LastModified"
        ]  # We can use this since no modification will be applied


_instance: Optional[SnapshotsDAO] = None


def create_snapshots_dao() -> SnapshotsDAO:
    """
    Creates an snapshots dao instance

    """
    global _instance

    if _instance:
        return _instance

    if settings.snapshots_provider == "local":
        _instance = LocalSnapshotsDAOImpl(folder=settings.snapshots_path)
    elif settings.snapshots_provider == "s3":
        _instance = S3SnapshotsDAOImpl(bucket_name=settings.snapshots_s3_bucket)
    else:
        raise ValueError(
            f"Unknown provider [{settings.snapshots_provider}]. Available values are : local, s3"
        )
    return _instance
