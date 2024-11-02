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

from typing import Dict, List, Optional

from pydantic import field_validator, Field

from argilla._models._settings._questions._base import QuestionSettings, QuestionBaseModel


class RankingQuestionSettings(QuestionSettings):
    type: str = "ranking"

    options: List[Dict[str, Optional[str]]] = Field(default_factory=list, validate_default=True)

    @field_validator("options", mode="before")
    @classmethod
    def __values_are_unique(cls, options: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
        """Ensure that values are unique"""

        unique_values = list(set([option["value"] for option in options]))
        if len(unique_values) != len(options):
            raise ValueError("All values must be unique")

        return options


class RankingQuestionModel(QuestionBaseModel):
    settings: RankingQuestionSettings
