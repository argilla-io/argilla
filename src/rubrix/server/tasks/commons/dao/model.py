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

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from rubrix.server.metrics.model import DatasetMetricResults


class RecordSearch(BaseModel):
    """
    Dao search

    Attributes:
    -----------

    query:
        The elasticsearch search query portion
    sort:
        The elasticsearch sort order
    aggregations:
        The elasticsearch search aggregations
    """

    query: Optional[Dict[str, Any]]
    sort: List[Dict[str, Any]] = Field(default_factory=list)
    aggregations: Optional[Dict[str, Any]]


class RecordSearchResults(BaseModel):
    """
    Dao search results

    Attributes:
    -----------

    total: int
        The total of query results
    records: List[T]
        List of records retrieved for the pagination configuration
    aggregations: Optional[Dict[str, Dict[str, Any]]]
        The query aggregations grouped by task. Optional
    words: Optional[Dict[str, int]]
        The words cloud aggregations
    metadata: Optional[Dict[str, int]]
        Metadata fields aggregations
    metrics: Optional[List[DatasetMetricResults]]
        Calculated metrics for search
    """

    total: int
    records: List[Dict[str, Any]]
    aggregations: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict)
    words: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, int]] = None
    metrics: Optional[List[DatasetMetricResults]] = Field(default_factory=list)
