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

from typing import TYPE_CHECKING, List, Optional, Union

from argilla_v1.client.feedback.schemas.enums import QuestionTypes
from argilla_v1.pydantic_v1 import (
    BaseModel,
    StrictInt,
    StrictStr,
    confloat,
    conint,
    constr,
    parse_obj_as,
    root_validator,
)

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.questions import QuestionSchema


class RankingValueSchema(BaseModel):
    """Schema for the `RankingQuestion` response value for a `RankingQuestion`. Note that
    we may have more than one record in the same rank.

    Args:
        value: The value of the record.
        rank: The rank of the record.
    """

    value: StrictStr
    rank: Optional[conint(ge=1)] = None


class SpanValueSchema(BaseModel):
    """Schema for the `SpanQuestion` response value for a `SpanQuestion`.

    Args:
        label: The label value of the span.
        start: The start of the span.
        end: The end of the span.
        score: The score of the span.
    """

    label: constr(min_length=1)
    start: conint(ge=0)
    end: conint(ge=0)
    score: Optional[confloat(ge=0.0, le=1.0)] = None

    @root_validator
    def check_span(cls, values):
        if values["end"] <= values["start"]:
            raise ValueError("The end of the span must be greater than the start.")
        return values


ResponseValue = Union[
    StrictStr,
    StrictInt,
    List[str],
    List[dict],
    List[RankingValueSchema],
    List[SpanValueSchema],
]

RESPONSE_VALUE_FOR_QUESTION_TYPE = {
    QuestionTypes.text: str,
    QuestionTypes.label_selection: str,
    QuestionTypes.multi_label_selection: List[str],
    QuestionTypes.ranking: List[RankingValueSchema],
    QuestionTypes.rating: int,
    QuestionTypes.span: List[SpanValueSchema],
}


def parse_value_response_for_question(question: "QuestionSchema", value: ResponseValue) -> ResponseValue:
    question_type = question.type
    response_type = RESPONSE_VALUE_FOR_QUESTION_TYPE[question_type]

    if isinstance(value, (dict, list)):
        return parse_obj_as(response_type, value)
    elif not isinstance(value, response_type):
        raise ValueError(f"Value {value} is not valid for question type {question_type}. Expected {response_type}.")

    return value


def normalize_response_value(value: ResponseValue) -> ResponseValue:
    """Normalize the response value."""
    if not isinstance(value, list) or not all([isinstance(v, dict) for v in value]):
        return value

    new_value = []
    for v in value:
        if "start" in v and "end" in v:
            new_value.append(SpanValueSchema(**v))
        elif "value" in v:
            new_value.append(RankingValueSchema(**v))
        else:
            raise ValueError("Invalid value", value)
    return new_value
