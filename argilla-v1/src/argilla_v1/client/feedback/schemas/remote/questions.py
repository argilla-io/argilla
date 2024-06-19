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

from argilla_v1.client.feedback.schemas import QuestionTypes
from argilla_v1.client.feedback.schemas.enums import LabelsOrder
from argilla_v1.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    SpanLabelOption,
    SpanQuestion,
    TextQuestion,
)
from argilla_v1.client.feedback.schemas.remote.shared import RemoteSchema

if TYPE_CHECKING:
    from argilla_v1.client.sdk.v1.datasets.models import FeedbackQuestionModel


class RemoteTextQuestion(TextQuestion, RemoteSchema):
    def to_local(self) -> TextQuestion:
        return TextQuestion(
            name=self.name,
            title=self.title,
            description=self.description,
            required=self.required,
            use_markdown=self.use_markdown,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteTextQuestion":
        return RemoteTextQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            description=payload.description,
            required=payload.required,
            use_markdown=payload.settings["use_markdown"],
        )


class RemoteRatingQuestion(RatingQuestion, RemoteSchema):
    def to_local(self) -> RatingQuestion:
        return RatingQuestion(
            name=self.name,
            title=self.title,
            description=self.description,
            required=self.required,
            values=self.values,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteRatingQuestion":
        return RemoteRatingQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            description=payload.description,
            required=payload.required,
            values=[option["value"] for option in payload.settings["options"]],
        )


def _parse_options_from_api(payload: "FeedbackQuestionModel") -> Union[List[str], Dict[str, str]]:
    if all([label["value"] == label["text"] for label in payload.settings["options"]]):
        return [label["value"] for label in payload.settings["options"]]
    else:
        return {label["value"]: label["text"] for label in payload.settings["options"]}


class RemoteLabelQuestion(LabelQuestion, RemoteSchema):
    def to_local(self) -> LabelQuestion:
        return LabelQuestion(
            name=self.name,
            title=self.title,
            description=self.description,
            required=self.required,
            labels=self.labels,
            visible_labels=self.visible_labels,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteLabelQuestion":
        return RemoteLabelQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            description=payload.description,
            required=payload.required,
            labels=_parse_options_from_api(payload),
            visible_labels=payload.settings["visible_options"],
        )


class RemoteMultiLabelQuestion(MultiLabelQuestion, RemoteSchema):
    def to_local(self) -> MultiLabelQuestion:
        return MultiLabelQuestion(
            name=self.name,
            title=self.title,
            description=self.description,
            required=self.required,
            labels=self.labels,
            visible_labels=self.visible_labels,
            labels_order=self.labels_order,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteMultiLabelQuestion":
        return RemoteMultiLabelQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            description=payload.description,
            required=payload.required,
            labels=_parse_options_from_api(payload),
            visible_labels=payload.settings["visible_options"],
            labels_order=payload.settings.get("options_order", LabelsOrder.natural),
        )


class RemoteRankingQuestion(RankingQuestion, RemoteSchema):
    def to_local(self) -> RankingQuestion:
        return RankingQuestion(
            name=self.name,
            title=self.title,
            description=self.description,
            required=self.required,
            values=self.values,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteRankingQuestion":
        return RemoteRankingQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            description=payload.description,
            required=payload.required,
            values=_parse_options_from_api(payload),
        )


class RemoteSpanQuestion(SpanQuestion, RemoteSchema):
    def to_local(self) -> SpanQuestion:
        return SpanQuestion(
            name=self.name,
            title=self.title,
            field=self.field,
            required=self.required,
            labels=self.labels,
            visible_labels=self.visible_labels,
            allow_overlapping=self.allow_overlapping,
        )

    @classmethod
    def _parse_options_from_api(cls, options: List[Dict[str, str]]) -> List[SpanLabelOption]:
        return [SpanLabelOption(value=option["value"], text=option["text"]) for option in options]

    @classmethod
    def from_api(cls, payload: "FeedbackQuestionModel") -> "RemoteSpanQuestion":
        question_settings = payload.settings
        return RemoteSpanQuestion(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            field=question_settings["field"],
            required=payload.required,
            visible_labels=question_settings["visible_options"],
            labels=cls._parse_options_from_api(question_settings["options"]),
            allow_overlapping=question_settings["allow_overlapping"],
        )


AllowedRemoteQuestionTypes = Union[
    RemoteTextQuestion,
    RemoteRatingQuestion,
    RemoteLabelQuestion,
    RemoteMultiLabelQuestion,
    RemoteRankingQuestion,
    RemoteSpanQuestion,
]

QUESTION_TYPE_TO_QUESTION = {
    QuestionTypes.text: RemoteTextQuestion,
    QuestionTypes.rating: RemoteRatingQuestion,
    QuestionTypes.label_selection: RemoteLabelQuestion,
    QuestionTypes.multi_label_selection: RemoteMultiLabelQuestion,
    QuestionTypes.ranking: RemoteRankingQuestion,
    QuestionTypes.span: RemoteSpanQuestion,
}
