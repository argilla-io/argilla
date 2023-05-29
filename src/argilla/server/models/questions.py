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
from typing import Any, List, Union

from pydantic import BaseModel, Field, parse_obj_as
from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from typing import Annotated, Literal
except ImportError:
    from typing_extensions import Annotated, Literal


class QuestionType(str, Enum):
    text = "text"
    rating = "rating"


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


class RatingQuestionSettings(BaseQuestionSettings):
    type: Literal[QuestionType.rating]
    options: List[RatingQuestionSettingsOption]

    @property
    def option_values(self) -> List[int]:
        return [option.value for option in self.options]

    def check_response(self, response: ResponseValue):
        if response.value not in self.option_values:
            raise ValueError(f"{response.value!r} is not a valid option.\nValid options are: {self.option_values!r}")


QuestionSettings = Annotated[Union[TextQuestionSettings, RatingQuestionSettings], Field(..., discriminator="type")]
