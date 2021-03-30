import datetime

from pydantic import BaseModel


class CreationDatasetSnapshot(BaseModel):
    """
    Creation dataset snapshot information

    Attributes:
    -----------
    id: str
        Snapshot id
    format: str
        The stored dataset format. Default="json"
    """

    id: str
    format: str = "json"


class DatasetSnapshotDB(CreationDatasetSnapshot):
    """

    Stored dataset snapshot data model

    Attributes:
    -----------

    uri: str
        The access uri to snapshot dataset
    task: str
        The snapshot task
    creation_date:
        THe snapshot creation date
    """

    uri: str
    task: str
    creation_date: datetime.datetime


class DatasetSnapshot(DatasetSnapshotDB):
    """
    Complete data model for dataset snapshot.
    """

    pass
