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

from typing import Dict, List, Optional, ClassVar

from pydantic import field_validator, Field, model_validator

from argilla._models._settings._questions._base import QuestionSettings, QuestionBaseModel

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


class LabelQuestionSettings(QuestionSettings):
    type: str = "label_selection"

    _MIN_VISIBLE_OPTIONS: ClassVar[int] = 3

    options: List[Dict[str, Optional[str]]] = Field(default_factory=list, validate_default=True)
    visible_options: Optional[int] = Field(None, validate_default=True, ge=_MIN_VISIBLE_OPTIONS)

    @field_validator("options", mode="before")
    @classmethod
    def __labels_are_unique(cls, options: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
        """Ensure that labels are unique"""

        unique_labels = list(set([option["value"] for option in options]))
        if len(unique_labels) != len(options):
            raise ValueError("All labels must be unique")
        return options

    @model_validator(mode="after")
    def __validate_visible_options(self) -> "Self":
        if self.visible_options is None and self.options and len(self.options) >= self._MIN_VISIBLE_OPTIONS:
            self.visible_options = len(self.options)
        return self


class LabelQuestionModel(QuestionBaseModel):
    settings: LabelQuestionSettings
