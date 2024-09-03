# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from typing import Literal, Any, Dict
from typing import Dict, Any, Literal

from argilla._models._settings._task_distribution import OverlapTaskDistributionModel


class OverlapTaskDistribution:
    """The task distribution settings class.

    This task distribution defines a number of submitted responses required to complete a record.

    Parameters:
        min_submitted (int): The number of min. submitted responses to complete the record
    """

    strategy: Literal["overlap"] = "overlap"

    def __init__(self, min_submitted: int):
        self._model = OverlapTaskDistributionModel(min_submitted=min_submitted, strategy=self.strategy)

    def __repr__(self) -> str:
        return f"OverlapTaskDistribution(min_submitted={self.min_submitted})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._model == other._model

    @classmethod
    def default(cls) -> "OverlapTaskDistribution":
        return cls(min_submitted=1)

    @property
    def min_submitted(self):
        return self._model.min_submitted

    @min_submitted.setter
    def min_submitted(self, value: int):
        self._model.min_submitted = value

    @classmethod
    def from_model(cls, model: OverlapTaskDistributionModel) -> "OverlapTaskDistribution":
        return cls(min_submitted=model.min_submitted)

    @classmethod
    def from_dict(cls, dict: Dict[str, Any]) -> "OverlapTaskDistribution":
        return cls.from_model(OverlapTaskDistributionModel.model_validate(dict))

    def to_dict(self):
        return self._model.model_dump()

    def _api_model(self) -> OverlapTaskDistributionModel:
        return self._model


TaskDistribution = OverlapTaskDistribution
