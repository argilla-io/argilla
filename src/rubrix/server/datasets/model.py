"""
Dataset models definition
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field
from rubrix.server.tasks.commons import TaskType


class UpdateDatasetRequest(BaseModel):
    """
    Modifiable fields for dataset

    Attributes:
    -----------
    tags:
        Dataset tags used for better organize or classify information
    metadata:
        Extra information that could be interested to include
    """

    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreationDatasetRequest(UpdateDatasetRequest):
    """
    Fields for dataset creation

    name: str
        the  dataset name
    task:
        The dataset task type. Deprecated
    """

    name: str = Field(regex="^(?!-|_)[a-z0-9-_]+$")


class DatasetDB(CreationDatasetRequest):
    """
    Low level dataset data model

    Attributes:
    -----------
    task:
        The dataset task type. Deprecated
    owner:
        The dataset owner
    created_at:
        The dataset creation date
    last_updated:
        The last modification date
    """

    task: TaskType
    owner: str = None
    created_at: datetime = None
    last_updated: datetime = None

    @property
    def id(self) -> str:
        """The dataset id. Compounded by owner and name"""
        if self.owner:
            return f"{self.owner}.{self.name}"
        return self.name


class Dataset(DatasetDB):
    """Dataset used for response output"""

    pass
