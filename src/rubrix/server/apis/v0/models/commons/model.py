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
from typing import Any, Dict, Generic, TypeVar

from fastapi import Query
from pydantic import validator
from pydantic.generics import GenericModel

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.apis.v0.helpers import flatten_dict
from rubrix.server.commons.models import TaskStatus
from rubrix.server.services.search.model import (
    BaseSearchResults,
    BaseSearchResultsAggregations,
    QueryRange,
)
from rubrix.server.services.search.model import SortableField as _SortableField
from rubrix.server.services.tasks.commons import (
    Annotation,
    BaseAnnotation,
    BaseRecordDB,
    BulkResponse,
    EsRecordDataFieldNames,
    PredictionStatus,
    TaskType,
)
from rubrix.utils import limit_value_length


class SortableField(_SortableField):
    pass


@dataclass
class PaginationParams:
    """Query pagination params"""

    limit: int = Query(50, gte=0, le=1000, description="Response records limit")
    from_: int = Query(
        0, ge=0, le=10000, alias="from", description="Record sequence from"
    )


# TODO(@frascuchon):  Move this shit to the server.commons.models module
class BaseRecord(BaseRecordDB, GenericModel, Generic[Annotation]):
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


Record = TypeVar("Record", bound=BaseRecord)


class ScoreRange(QueryRange):
    pass


__ALL__ = [
    QueryRange,
    BaseSearchResults,
    BaseSearchResultsAggregations,
    Annotation,
    TaskStatus,
    TaskType,
    EsRecordDataFieldNames,
    BaseAnnotation,
    PredictionStatus,
    BulkResponse,
]
