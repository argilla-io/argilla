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
    """

    uri: str


class DatasetSnapshot(DatasetSnapshotDB):
    """
    Complete data model for dataset snapshot.
    """

    pass
