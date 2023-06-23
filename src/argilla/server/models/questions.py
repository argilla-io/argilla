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
from typing import Any, Generic, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, Field

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


class QuestionType(str, Enum):
    text = "text"
    rating = "rating"
    label_selection = "label_selection"
    multi_label_selection = "multi_label_selection"
    ranking = "ranking"


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


class ValueTextQuestionSettingsOption(BaseModel):
    value: str
    text: str
    description: Optional[str] = None


class LabelSelectionQuestionSettings(ValidOptionCheckerMixin[str]):
    type: Literal[QuestionType.label_selection]
    options: List[ValueTextQuestionSettingsOption]
    visible_options: Optional[int] = None


def _are_all_elements_in_list(elements: List[T], list_: List[T]) -> List[T]:
    return sorted(list(set(elements) - set(list_)))


class MultiLabelSelectionQuestionSettings(LabelSelectionQuestionSettings):
    type: Literal[QuestionType.multi_label_selection]

    def check_response(self, response: ResponseValue):
        if not isinstance(response.value, list):
            raise ValueError(
                f"This MultiLabelSelection question expects a list of values, found {type(response.value)}"
            )

        if len(response.value) == 0:
            raise ValueError("This MultiLabelSelection question expects a list of values, found empty list")

        unique_values = set(response.value)
        if len(unique_values) != len(response.value):
            raise ValueError(
                "This MultiLabelSelection question expects a list of unique values, but duplicates were found"
            )

        invalid_options = _are_all_elements_in_list(response.value, self.option_values)
        if invalid_options:
            raise ValueError(
                f"{invalid_options!r} are not valid options for this MultiLabelSelection question.\nValid options are:"
                f" {self.option_values!r}"
            )


class RankingQuestionSettings(ValidOptionCheckerMixin[str]):
    type: Literal[QuestionType.ranking]
    options: List[ValueTextQuestionSettingsOption]

    @property
    def rank_values(self) -> List[int]:
        return list(range(1, len(self.option_values) + 1))

    def check_response(self, response: ResponseValue):
        if not isinstance(response.value, list):
            raise ValueError(f"This Ranking question expects a list of values, found {type(response.value)}")

        if len(response.value) != len(self.option_values):
            raise ValueError(
                f"This Ranking question expects a list containing {len(self.option_values)} values, found a list of"
                f" {len(response.value)} values"
            )

        values = []
        ranks = []
        for response_option in response.value:
            values.append(response_option.get("value"))
            ranks.append(response_option.get("rank"))

        invalid_ranks = _are_all_elements_in_list(ranks, self.rank_values)
        if invalid_ranks:
            raise ValueError(
                f"{invalid_ranks!r} are not valid ranks for this Ranking question.\nValid ranks are:"
                f" {self.rank_values!r}"
            )

        invalid_values = _are_all_elements_in_list(values, self.option_values)
        if invalid_values:
            raise ValueError(
                f"{invalid_values!r} are not valid options for this Ranking question.\nValid options are:"
                f" {self.option_values!r}"
            )

        unique_values = set(values)
        if len(response.value) != len(unique_values):
            raise ValueError("This Ranking question expects a list of unique values, but duplicates were found")


QuestionSettings = Annotated[
    Union[
        TextQuestionSettings,
        RatingQuestionSettings,
        LabelSelectionQuestionSettings,
        MultiLabelSelectionQuestionSettings,
        RankingQuestionSettings,
    ],
    Field(..., discriminator="type"),
]
