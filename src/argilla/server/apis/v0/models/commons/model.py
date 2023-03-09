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

from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from argilla.server.services.search.model import (
    ServiceQueryRange,
    ServiceSearchResultsAggregations,
    ServiceSortableField,
)
from argilla.server.services.tasks.commons import (
    ServiceBaseAnnotation,
    ServiceBaseRecord,
    ServiceBaseRecordInputs,
)


class SortableField(ServiceSortableField):
    pass


class BaseAnnotation(ServiceBaseAnnotation):
    pass


Annotation = TypeVar("Annotation", bound=BaseAnnotation)


class BaseRecordInputs(ServiceBaseRecordInputs[Annotation], Generic[Annotation]):
    def extended_fields(self) -> Dict[str, Any]:
        return {}


class BaseRecord(ServiceBaseRecord[Annotation], Generic[Annotation]):
    pass


class ScoreRange(ServiceQueryRange):
    pass


_Record = TypeVar("_Record", bound=BaseRecord)


class BulkResponse(BaseModel):
    dataset: str
    processed: int
    failed: int = 0


class BaseSearchResults(GenericModel, Generic[_Record, ServiceSearchResultsAggregations]):
    total: int = 0
    records: List[_Record] = Field(default_factory=list)
    aggregations: ServiceSearchResultsAggregations = None
