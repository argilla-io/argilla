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
from typing import Any, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

try:
    from typing import Annotated, Literal
except ImportError:
    from typing_extensions import Annotated, Literal


class QuestionType(str, Enum):
    text = "text"
    rating = "rating"
    label_selection = "label_selection"
    multi_label_selection = "multi_label_selection"


class ResponseValue(BaseModel):
    value: Any


class BaseQuestionSettings(BaseModel):
    def check_response(self, response: ResponseValue):
        pass


class TextQuestionSettings(BaseQuestionSettings):
    type: Literal[QuestionType.text]
    use_markdown: bool = False

    def check_response(self, response: ResponseValue):
        if not isinstance(response.value, str):
            raise ValueError(f"Expected text value, found {type(response.value)}")


class RatingQuestionSettingsOption(BaseModel):
    value: int


T = TypeVar("T")


class ValidOptionCheckerMixin(BaseQuestionSettings, Generic[T]):
    @property
    def option_values(self) -> List[T]:
        return [option.value for option in self.options]

    def check_response(self, response: ResponseValue):
        if response.value not in self.option_values:
            raise ValueError(f"{response.value!r} is not a valid option.\nValid options are: {self.option_values!r}")


class RatingQuestionSettings(ValidOptionCheckerMixin[int]):
    type: Literal[QuestionType.rating]
    options: List[RatingQuestionSettingsOption]


class LabelSelectionQuestionSettingsOption(BaseModel):
    value: str
    text: str
    description: Optional[str] = None


class LabelSelectionQuestionSettings(ValidOptionCheckerMixin[str]):
    type: Literal[QuestionType.label_selection]
    options: List[LabelSelectionQuestionSettingsOption]
    visible_options: Optional[int] = None


class MultiLabelSelectionQuestionSettings(LabelSelectionQuestionSettings):
    type: Literal[QuestionType.multi_label_selection]

    def check_response(self, response: ResponseValue):
        if not isinstance(response.value, list):
            raise ValueError(f"Expected list of values, found {type(response.value)}")
        if len(response.value) == 0:
            raise ValueError("Expected list of values, found empty list")
        invalid_options = sorted(list(set(response.value) - set(self.option_values)))
        if invalid_options:
            raise ValueError(f"{invalid_options!r} are not valid options.\nValid options are: {self.option_values!r}")


QuestionSettings = Annotated[
    Union[
        TextQuestionSettings,
        RatingQuestionSettings,
        LabelSelectionQuestionSettings,
        MultiLabelSelectionQuestionSettings,
    ],
    Field(..., discriminator="type"),
]
