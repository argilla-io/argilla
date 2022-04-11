from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from rubrix.server.api.v1.constants import DATASET_NAME_PATTERN
from rubrix.server.api.v1.models.commons.params import build_pagination_params

DatasetSettings = TypeVar("DatasetSettings")


class DatasetUpdate(BaseModel):
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetCreate(DatasetUpdate):
    name: str = Field(regex=DATASET_NAME_PATTERN)


class DatasetCopy(DatasetCreate):
    target_workspace: Optional[str] = None


class TextClassificationSettings(BaseModel):
    multi_label: bool = Field(
        default=False,
        description="If true, dataset is ready to multi-label text classification",
    )
    allowed_labels: Optional[Union[List[str], List[int]]] = None


class TextClassificationDatasetCreate(DatasetCreate):
    settings: TextClassificationSettings = Field(
        default_factory=TextClassificationSettings
    )


class TokenClassificationDatasetCreate(DatasetCreate):
    pass


class Text2TextDatasetCreate(DatasetCreate):
    pass


class BaseDataset(BaseModel):

    name: str
    owner: Optional[str] = None
    created_at: datetime = None
    last_updated: datetime = None
    created_by: str = None

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


class TextClassificationDataset(BaseDataset, TextClassificationDatasetCreate):
    pass


class TokenClassificationDataset(BaseDataset, TokenClassificationDatasetCreate):
    pass


class Text2TextDataset(BaseDataset, Text2TextDatasetCreate):
    pass


Dataset = Union[
    TextClassificationDataset,
    TokenClassificationDataset,
    Text2TextDataset,
]


class DatasetsList(BaseModel):
    total: int
    data: List[Dataset]


PaginationParams = build_pagination_params(item_type="dataset")
