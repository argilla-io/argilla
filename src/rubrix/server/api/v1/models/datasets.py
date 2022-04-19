from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from rubrix.server.api.v1.constants import DATASET_NAME_PATTERN
from rubrix.server.api.v1.models.commons.params import build_pagination_params
from rubrix.server.api.v1.models.commons.task import TaskType

DatasetSettings = TypeVar("DatasetSettings")


class DatasetUpdate(BaseModel):
    tags: Dict[str, str] = Field(
        default_factory=dict, description="Public tags defined for dataset"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extra metadata info related to dataset"
    )


class DatasetCreate(DatasetUpdate):
    name: str = Field(regex=DATASET_NAME_PATTERN, description="The dataset name")


class DatasetCopy(DatasetCreate):
    target_workspace: Optional[str] = Field(
        default=None, description="Target workspace used for copied dataset"
    )


class TextClassificationSettings(BaseModel):
    multi_label: bool = Field(
        default=False,
        description="If true, dataset is ready to multi-label text classification",
    )
    allowed_labels: Optional[Union[List[str], List[int]]] = Field(
        None, description="Allowed list of labels for data annotation in the dataset"
    )


class TextClassificationDatasetCreate(DatasetCreate):
    settings: TextClassificationSettings = Field(
        default_factory=TextClassificationSettings,
        description="Settings for text classification datasets",
    )


class TokenClassificationDatasetCreate(DatasetCreate):
    pass


class Text2TextDatasetCreate(DatasetCreate):
    pass


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


class TextClassificationDataset(AbstractBaseDataset, TextClassificationDatasetCreate):
    task: TaskType = Field(default=TaskType.text_classification, const=True)


class TokenClassificationDataset(AbstractBaseDataset, TokenClassificationDatasetCreate):
    task: TaskType = Field(default=TaskType.token_classification, const=True)


class Text2TextDataset(AbstractBaseDataset, Text2TextDatasetCreate):
    task: TaskType = Field(default=TaskType.text2text, const=True)


Dataset = Union[
    TextClassificationDataset,
    TokenClassificationDataset,
    Text2TextDataset,
]


class DatasetsList(BaseModel):
    total: int = Field(description="Total number of datasets")
    data: List[Dataset] = Field(description="The dataset list")


PaginationParams = build_pagination_params(item_type="dataset")
