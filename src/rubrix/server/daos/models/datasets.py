from datetime import datetime
from typing import Any, Dict, Optional, TypeVar

from pydantic import BaseModel, Field

from rubrix._constants import DATASET_NAME_REGEX_PATTERN
from rubrix.server.commons.models import TaskType


class BaseDatasetDB(BaseModel):
    name: str = Field(regex=DATASET_NAME_REGEX_PATTERN)
    task: TaskType
    owner: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = None
    created_by: str = Field(
        None, description="The Rubrix user that created the dataset"
    )
    last_updated: datetime = None

    @classmethod
    def build_dataset_id(cls, name: str, owner: Optional[str] = None) -> str:
        """Build a dataset id for a given name and owner"""
        if owner:
            return f"{owner}.{name}"
        return name

    @property
    def id(self) -> str:
        """The dataset id. Compounded by owner and name"""
        return self.build_dataset_id(self.name, self.owner)


class BaseDatasetSettingsDB(BaseModel):
    pass


DatasetDB = TypeVar("DatasetDB", bound=BaseDatasetDB)
DatasetSettingsDB = TypeVar("DatasetSettingsDB", bound=BaseDatasetSettingsDB)
