"""
Common data models for api operations
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Union

from fastapi import Query
from pydantic import BaseModel, Field, validator


class BulkResponse(BaseModel):
    """
    Data info for bulk results

    Attributes
    ----------

    dataset:
        The dataset name
    processed:
        Number of records in bulk
    failed:
        Number of failed records
    """

    dataset: str
    processed: int
    failed: int = 0


@dataclass
class PaginationParams:
    """Query pagination params"""

    limit: int = Query(50, gte=0, le=1000, description="Response records limit")
    from_: int = Query(0, ge=0, alias="from", description="Record sequence from")


class SortOrder(str, Enum):
    """Available sort search modes """

    ASC = "asc"
    DESC = "desc"


class SortableField(str, Enum):
    """Default selectable sortable field"""

    predicted_as = "predicted_as"
    annotated_as = "annotated_as"
    annotated_by = "annotated_by"
    predicted_by = "predicted_by"
    status = "status"
    predicted = "predicted"


class SortParam(BaseModel):
    """Single sort param criteria"""

    by: Union[SortableField, str]
    order: SortOrder = Field(default_factory=lambda: SortOrder.ASC)

    __sort_param_name_pattern__: ClassVar = re.compile(r"(metadata\.\S+)")

    @validator("by")
    def check_valid_param_name(cls, value: Union[str, SortableField]):
        """Fastapi validator checking the sort param name"""
        if isinstance(value, SortableField):
            return value
        try:
            return SortableField(value)
        except Exception:
            assert cls.__sort_param_name_pattern__.match(
                value
            ), f"Wrong field name {value}. Accepted pattern 'metadata.*'"
