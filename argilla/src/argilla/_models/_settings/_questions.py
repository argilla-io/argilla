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

from typing import Annotated, Union, Optional, ClassVar, List, Dict, Literal
from uuid import UUID

from pydantic import ConfigDict, field_validator, Field, BaseModel, model_validator, field_serializer
from pydantic_core.core_schema import ValidationInfo

from argilla._models import ResourceModel

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


class LabelQuestionSettings(BaseModel):
    type: Literal["label_selection"] = "label_selection"

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


class MultiLabelQuestionSettings(LabelQuestionSettings):
    type: Literal["multi_label_selection"] = "multi_label_selection"
    options_order: Literal["natural", "suggestion"] = Field("natural", description="The order of the labels in the UI.")


class RankingQuestionSettings(BaseModel):
    type: Literal["ranking"] = "ranking"

    options: List[Dict[str, Optional[str]]] = Field(default_factory=list, validate_default=True)

    @field_validator("options", mode="before")
    @classmethod
    def __values_are_unique(cls, options: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
        """Ensure that values are unique"""

        unique_values = list(set([option["value"] for option in options]))
        if len(unique_values) != len(options):
            raise ValueError("All values must be unique")

        return options


class RatingQuestionSettings(BaseModel):
    type: Literal["rating"] = "rating"

    options: List[dict] = Field(..., validate_default=True)

    @field_validator("options", mode="before")
    @classmethod
    def __values_are_unique(cls, options: List[dict]) -> List[dict]:
        """Ensure that values are unique"""

        unique_values = list(set([option["value"] for option in options]))
        if len(unique_values) != len(options):
            raise ValueError("All values must be unique")

        return options


class SpanQuestionSettings(BaseModel):
    type: Literal["span"] = "span"

    _MIN_VISIBLE_OPTIONS: ClassVar[int] = 3

    allow_overlapping: bool = False
    field: Optional[str] = None
    options: List[Dict[str, Optional[str]]] = Field(default_factory=list, validate_default=True)
    visible_options: Optional[int] = Field(None, validate_default=True, ge=_MIN_VISIBLE_OPTIONS)

    @field_validator("options", mode="before")
    @classmethod
    def __values_are_unique(cls, options: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
        """Ensure that values are unique"""

        unique_values = list(set([option["value"] for option in options]))
        if len(unique_values) != len(options):
            raise ValueError("All values must be unique")

        return options

    @model_validator(mode="after")
    def __validate_visible_options(self) -> "Self":
        if self.visible_options is None and self.options and len(self.options) >= self._MIN_VISIBLE_OPTIONS:
            self.visible_options = len(self.options)
        return self


class TextQuestionSettings(BaseModel):
    type: Literal["text"] = "text"

    use_markdown: bool = False


QuestionSettings = Annotated[
    Union[
        LabelQuestionSettings,
        MultiLabelQuestionSettings,
        RankingQuestionSettings,
        RatingQuestionSettings,
        SpanQuestionSettings,
        TextQuestionSettings,
    ],
    Field(..., discriminator="type"),
]


class QuestionModel(ResourceModel):
    name: str
    settings: QuestionSettings

    title: str = Field(None, validate_default=True)
    description: Optional[str] = None
    required: bool = True

    dataset_id: Optional[UUID] = None

    @field_validator("title", mode="before")
    @classmethod
    def _title_default(cls, title, info: ValidationInfo):
        validated_title = title or info.data["name"]
        return validated_title

    @property
    def type(self) -> str:
        return self.settings.type

    @field_serializer("id", "dataset_id", when_used="unless-none")
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    model_config = ConfigDict(validate_assignment=True)
