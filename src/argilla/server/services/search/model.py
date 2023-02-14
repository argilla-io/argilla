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

from typing import Any, Dict, List, TypeVar

from pydantic import BaseModel, Field

from argilla.server.daos.backend.search.model import (
    BaseRecordsQuery,
    QueryRange,
    SortableField,
    SortConfig,
)
from argilla.server.services.tasks.commons import ServiceRecord


class ServiceBaseRecordsQuery(BaseRecordsQuery):
    pass


class ServiceSortConfig(SortConfig):
    pass


class ServiceSortableField(SortableField):
    """Sortable field structure"""

    pass


class ServiceQueryRange(QueryRange):
    pass


class ServiceScoreRange(ServiceQueryRange):
    pass


class ServiceBaseSearchResultsAggregations(BaseModel):
    predicted_as: Dict[str, int] = Field(default_factory=dict)
    annotated_as: Dict[str, int] = Field(default_factory=dict)
    annotated_by: Dict[str, int] = Field(default_factory=dict)
    predicted_by: Dict[str, int] = Field(default_factory=dict)
    status: Dict[str, int] = Field(default_factory=dict)
    predicted: Dict[str, int] = Field(default_factory=dict)
    score: Dict[str, int] = Field(default_factory=dict)
    words: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


ServiceSearchResultsAggregations = TypeVar(
    "ServiceSearchResultsAggregations", bound=ServiceBaseSearchResultsAggregations
)


class ServiceSearchResults(BaseModel):
    total: int
    records: List[ServiceRecord]
    metrics: Dict[str, Any] = Field(default_factory=dict)


ServiceRecordsQuery = TypeVar("ServiceRecordsQuery", bound=ServiceBaseRecordsQuery)
