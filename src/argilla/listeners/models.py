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

import dataclasses
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from prodict import Prodict

from argilla.client.models import Record

if TYPE_CHECKING:
    from argilla.listeners import RGDatasetListener


@dataclasses.dataclass
class Search:
    """
    Search results for a single listener execution

    Args:
        total: The total number of records affected by the listener query
        query_params: The query parameters applied to the executed search
    """

    total: int
    query_params: Optional[Dict[str, Any]] = None


class Metrics(Prodict):
    """
    Metrics results for a single listener execution.

    The metrics object exposes the metrics configured for the listener as property values.
    For example, if you define a listener including the metric "F1", the results will be
    accessible as ``metrics.F1``
    """

    pass


@dataclasses.dataclass
class RGListenerContext:
    """
    The argilla listener execution context. This class keeps the context components related to a listener

    Args:

        listener: The argilla listener instance
        search: Search results for current execution
        metrics: Metrics results for current execution
        query_params: Dynamic parameters used in the listener query
    """

    listener: "RGDatasetListener" = dataclasses.field(repr=False, hash=False)
    search: Optional[Search] = None
    metrics: Optional[Metrics] = None
    query_params: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.__listener__ = self.listener
        del self.listener

    @property
    def dataset(self) -> str:
        """Computed property that returns the configured listener dataset name"""
        return self.__listener__.dataset

    @property
    def query(self) -> Optional[str]:
        """Computed property that returns the configured listener query string"""
        return self.__listener__.formatted_query


ListenerCondition = Callable[[Search, Optional[RGListenerContext]], bool]
ListenerAction = Union[
    Callable[[List[Record], RGListenerContext], bool],
    Callable[[RGListenerContext], bool],
]
