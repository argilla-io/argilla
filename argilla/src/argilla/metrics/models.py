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

import warnings
from typing import Any, Callable, Dict

from argilla.pydantic_v1 import BaseModel, PrivateAttr


# TODO(@frascuchon): Define as dataclasses.dataclass
class MetricSummary(BaseModel):
    """THe metric summary result data model"""

    data: Dict[str, Any]
    _build_visualization: Callable = PrivateAttr()

    def visualize(self):
        try:
            return self._build_visualization()
        except ModuleNotFoundError:
            warnings.warn("Please, install plotly in order to use this feature:\n> pip install plotly", stacklevel=2)

    @classmethod
    def new_summary(cls, data: Dict[str, Any], visualization: Callable) -> "MetricSummary":
        summary = cls(data=data)
        summary._build_visualization = visualization
        return summary
