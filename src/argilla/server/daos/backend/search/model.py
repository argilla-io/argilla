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

from enum import Enum
from typing import Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from argilla.server.commons.models import TaskStatus


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class QueryRange(BaseModel):

    range_from: float = Field(default=0.0, alias="from")
    range_to: float = Field(default=None, alias="to")

    class Config:
        allow_population_by_field_name = True


class SortableField(BaseModel):
    """Sortable field structure"""

    id: str
    order: SortOrder = SortOrder.asc


class SortConfig(BaseModel):
    shuffle: bool = False

    sort_by: List[SortableField] = Field(default_factory=list)
    valid_fields: List[str] = Field(default_factory=list)


class BaseQuery(BaseModel):
    pass


class BaseDatasetsQuery(BaseQuery):
    tasks: Optional[List[str]] = None
    owners: Optional[List[str]] = None
    include_no_owner: bool = None
    name: Optional[str] = None


class BaseRecordsQuery(BaseQuery):

    query_text: Optional[str] = None
    advanced_query_dsl: bool = False

    ids: Optional[List[Union[str, int]]]

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    status: List[TaskStatus] = Field(default_factory=list)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    has_annotation: Optional[bool] = None
    has_prediction: Optional[bool] = None


BackendQuery = TypeVar("BackendQuery", bound=BaseQuery)
BackendRecordsQuery = TypeVar("BackendRecordsQuery", bound=BaseRecordsQuery)
BackendDatasetsQuery = TypeVar("BackendDatasetsQuery", bound=BaseDatasetsQuery)
