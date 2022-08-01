#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Common model for task definitions
"""

from dataclasses import dataclass
from typing import Any, Dict, Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.helpers import flatten_dict
from rubrix.server.services.search.model import (
    ServiceQueryRange,
    ServiceSearchResultsAggregations,
    ServiceSortableField,
)
from rubrix.server.services.tasks.commons import (
    ServiceBaseAnnotation,
    ServiceBaseRecord,
    ServiceRecord,
)
from rubrix.utils import limit_value_length


class SortableField(ServiceSortableField):
    pass


@dataclass
class PaginationParams:
    """Query pagination params"""

    limit: int = Query(50, gte=0, le=1000, description="Response records limit")
    from_: int = Query(
        0, ge=0, le=10000, alias="from", description="Record sequence from"
    )


class BaseAnnotation(ServiceBaseAnnotation):
    pass


Annotation = TypeVar("Annotation", bound=BaseAnnotation)


class BaseRecord(ServiceBaseRecord[Annotation], Generic[Annotation]):
    """
    Minimal dataset record information

    Attributes:
    -----------

    id:
        The record id
    metadata:
        The metadata related to record
    event_timestamp:
        The timestamp when record event was triggered

    """

    @validator("metadata", pre=True)
    def flatten_metadata(cls, metadata: Dict[str, Any]):
        """
        A fastapi validator for flatten metadata dictionary

        Parameters
        ----------
        metadata:
            The metadata dictionary

        Returns
        -------
            A flatten version of metadata dictionary

        """
        if metadata:
            metadata = flatten_dict(metadata, drop_empty=True)
            metadata = limit_value_length(metadata, max_length=MAX_KEYWORD_LENGTH)
        return metadata


class ScoreRange(ServiceQueryRange):
    pass


_Record = TypeVar("_Record", bound=BaseRecord)


class BulkResponse(BaseModel):
    dataset: str
    processed: int
    failed: int = 0


class BaseSearchResults(
    GenericModel, Generic[_Record, ServiceSearchResultsAggregations]
):
    total: int = 0
    records: List[_Record] = Field(default_factory=list)
    aggregations: ServiceSearchResultsAggregations = None
