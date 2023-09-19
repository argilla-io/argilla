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

from typing import TYPE_CHECKING, Dict, List, Union
from uuid import UUID

from pydantic import BaseModel

from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)

if TYPE_CHECKING:
    from argilla.client.sdk.v1.datasets.models import FeedbackQuestionModel


class RemoteQuestionSchema(BaseModel):
    id: UUID

    class Config:
        allow_mutation = False


class RemoteTextQuestion(TextQuestion, RemoteQuestionSchema):
    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteTextQuestion":
        return RemoteTextQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            required=payload.required,
            type="text",
            use_markdown=payload.settings["use_markdown"],
        )


class RemoteRatingQuestion(RatingQuestion, RemoteQuestionSchema):
    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteRatingQuestion":
        return RemoteRatingQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            required=payload.required,
            type="rating",
            values=[option["value"] for option in payload.settings["options"]],
        )


def _parse_options_from_api(payload: "FeedbackQuestionModel") -> Union[List[str], Dict[str, str]]:
    if all([label["value"] == label["text"] for label in payload.settings["options"]]):
        return [label["value"] for label in payload.settings["options"]]
    else:
        return {label["value"]: label["text"] for label in payload.settings["options"]}


class RemoteLabelQuestion(LabelQuestion, RemoteQuestionSchema):
    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteLabelQuestion":
        return RemoteLabelQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            required=payload.required,
            type="label_selection",
            labels=_parse_options_from_api(payload),
            visible_labels=payload.settings["visible_options"],
        )


class RemoteMultiLabelQuestion(MultiLabelQuestion, RemoteQuestionSchema):
    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteLabelQuestion":
        return RemoteMultiLabelQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            required=payload.required,
            type="multi_label_selection",
            labels=_parse_options_from_api(payload),
            visible_labels=payload.settings["visible_options"],
        )


class RemoteRankingQuestion(RankingQuestion, RemoteQuestionSchema):
    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteLabelQuestion":
        return RemoteRankingQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            required=payload.required,
            type="ranking",
            values=_parse_options_from_api(payload),
        )
