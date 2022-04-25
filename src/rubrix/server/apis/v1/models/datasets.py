from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from rubrix.server.apis.v1.constants import DATASET_NAME_PATTERN
from rubrix.server.apis.v1.models.commons.params import build_pagination_params
from rubrix.server.apis.v1.models.commons.task import TaskType


class DatasetUpdate(BaseModel):
    tags: Dict[str, str] = Field(
        default_factory=dict, description="Public tags defined for dataset"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extra metadata info related to dataset"
    )


class DatasetCreate(DatasetUpdate):
    name: str = Field(regex=DATASET_NAME_PATTERN, description="The dataset name")


class AbstractBaseDataset(BaseModel):

    name: str = Field(description="The dataset name")
    owner: Optional[str] = Field(None, description="Owner workspace for dataset")
    created_at: datetime = Field(None, description="UTC creation datetime")
    last_updated: datetime = Field(
        None, description="Last UTC datetime where dataset was modified"
    )
    created_by: str = Field(
        None, description="The Rubrix user that created the dataset"
    )

    task: TaskType = Field(description="The dataset task type")


class Dataset(AbstractBaseDataset):
    pass


PaginationParams = build_pagination_params(item_type="dataset")
