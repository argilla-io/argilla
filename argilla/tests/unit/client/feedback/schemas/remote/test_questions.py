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

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

import pytest
from argilla_v1.client.feedback.schemas.enums import LabelsOrder, QuestionTypes
from argilla_v1.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla_v1.client.feedback.schemas.remote.questions import (
    RemoteLabelQuestion,
    RemoteMultiLabelQuestion,
    RemoteRankingQuestion,
    RemoteRatingQuestion,
    RemoteSpanQuestion,
    RemoteTextQuestion,
)
from argilla_v1.client.sdk.v1.datasets.models import FeedbackQuestionModel


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "required": True, "use_markdown": True},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {"type": "text", "use_markdown": True},
            },
        ),
        (
            {"name": "a", "title": "B", "description": "b", "required": False, "use_markdown": False},
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "settings": {"type": "text", "use_markdown": False},
            },
        ),
    ],
)
def test_remote_text_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    text_question = RemoteTextQuestion(**schema_kwargs)
    assert text_question.type == QuestionTypes.text
    assert text_question.server_settings == server_payload["settings"]
    assert text_question.to_server_payload() == server_payload

    local_text_question = text_question.to_local()
    assert isinstance(local_text_question, TextQuestion)
    assert local_text_question.type == QuestionTypes.text
    assert local_text_question.server_settings == server_payload["settings"]
    assert local_text_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackQuestionModel(
            id=uuid4(),
            name="a",
            title="A",
            description="Description",
            required=True,
            settings={"type": "text", "use_markdown": False},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackQuestionModel(
            id=uuid4(),
            name="b",
            title="B",
            description="Description",
            required=False,
            settings={"type": "text", "use_markdown": True},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_text_question_from_api(payload: FeedbackQuestionModel) -> None:
    text_question = RemoteTextQuestion.from_api(payload)
    assert text_question.type == QuestionTypes.text
    assert text_question.server_settings == payload.settings
    assert text_question.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "values": [1, 2, 3]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": 3}]},
            },
        ),
        (
            {"name": "a", "title": "B", "description": "b", "required": False, "values": [1, 2, 3]},
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "settings": {"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": 3}]},
            },
        ),
    ],
)
def test_remote_rating_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    rating_question = RemoteRatingQuestion(**schema_kwargs)
    assert rating_question.type == QuestionTypes.rating
    assert rating_question.server_settings == server_payload["settings"]
    assert rating_question.to_server_payload() == server_payload

    local_rating_question = rating_question.to_local()
    assert isinstance(local_rating_question, RatingQuestion)
    assert local_rating_question.type == QuestionTypes.rating
    assert local_rating_question.server_settings == server_payload["settings"]
    assert local_rating_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackQuestionModel(
            id=uuid4(),
            name="a",
            title="A",
            description="Description",
            required=True,
            settings={"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": 3}]},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackQuestionModel(
            id=uuid4(),
            name="b",
            title="B",
            description="Description",
            required=False,
            settings={"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": 3}]},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_rating_question_from_api(payload: FeedbackQuestionModel) -> None:
    rating_question = RemoteRatingQuestion.from_api(payload)
    assert rating_question.type == QuestionTypes.rating
    assert rating_question.server_settings == payload.settings
    assert rating_question.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "labels": ["a", "b", "c"]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"text": "a", "value": "a"}, {"text": "b", "value": "b"}, {"text": "c", "value": "c"}],
                    "visible_options": None,
                },
            },
        ),
        (
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "labels": {"a": "A", "b": "B", "c": "C"},
                "visible_labels": 3,
            },
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "settings": {
                    "type": "label_selection",
                    "options": [{"text": "A", "value": "a"}, {"text": "B", "value": "b"}, {"text": "C", "value": "c"}],
                    "visible_options": 3,
                },
            },
        ),
    ],
)
def test_remote_label_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    label_question = RemoteLabelQuestion(**schema_kwargs)
    assert label_question.type == QuestionTypes.label_selection
    assert label_question.server_settings == server_payload["settings"]
    assert label_question.to_server_payload() == server_payload

    local_label_question = label_question.to_local()
    assert isinstance(local_label_question, LabelQuestion)
    assert local_label_question.type == QuestionTypes.label_selection
    assert local_label_question.server_settings == server_payload["settings"]
    assert local_label_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackQuestionModel(
            id=uuid4(),
            name="a",
            title="A",
            required=True,
            description="Description",
            settings={
                "type": "label_selection",
                "options": [{"text": "a", "value": "a"}, {"text": "b", "value": "b"}, {"text": "c", "value": "c"}],
                "visible_options": None,
            },
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackQuestionModel(
            id=uuid4(),
            name="b",
            title="B",
            description="Description",
            required=False,
            settings={
                "type": "label_selection",
                "options": [{"text": "A", "value": "a"}, {"text": "B", "value": "b"}, {"text": "C", "value": "c"}],
                "visible_options": 3,
            },
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_label_question_from_api(payload: FeedbackQuestionModel) -> None:
    label_question = RemoteLabelQuestion.from_api(payload)
    assert label_question.type == QuestionTypes.label_selection
    assert label_question.server_settings == payload.settings
    assert label_question.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "labels": ["a", "b", "c"]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"text": "a", "value": "a"}, {"text": "b", "value": "b"}, {"text": "c", "value": "c"}],
                    "visible_options": None,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
        (
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "labels": {"a": "A", "b": "B", "c": "C"},
                "visible_labels": 3,
                "labels_order": LabelsOrder.suggestion,
            },
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"text": "A", "value": "a"}, {"text": "B", "value": "b"}, {"text": "C", "value": "c"}],
                    "visible_options": 3,
                    "options_order": LabelsOrder.suggestion,
                },
            },
        ),
    ],
)
def test_remote_multi_label_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    multi_label_question = RemoteMultiLabelQuestion(**schema_kwargs)
    assert multi_label_question.type == QuestionTypes.multi_label_selection
    assert multi_label_question.server_settings == server_payload["settings"]
    assert multi_label_question.to_server_payload() == server_payload

    local_multi_label_question = multi_label_question.to_local()
    assert isinstance(local_multi_label_question, MultiLabelQuestion)
    assert local_multi_label_question.type == QuestionTypes.multi_label_selection
    assert local_multi_label_question.server_settings == server_payload["settings"]
    assert local_multi_label_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackQuestionModel(
            id=uuid4(),
            name="a",
            title="A",
            description="Description",
            required=True,
            settings={
                "type": "multi_label_selection",
                "options": [{"text": "a", "value": "a"}, {"text": "b", "value": "b"}, {"text": "c", "value": "c"}],
                "visible_options": None,
                "options_order": LabelsOrder.natural,
            },
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackQuestionModel(
            id=uuid4(),
            name="b",
            title="B",
            description="Description",
            required=False,
            settings={
                "type": "multi_label_selection",
                "options": [{"text": "A", "value": "a"}, {"text": "B", "value": "b"}, {"text": "C", "value": "c"}],
                "visible_options": 3,
                "options_order": LabelsOrder.suggestion,
            },
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_multi_label_question_from_api(payload: FeedbackQuestionModel) -> None:
    multi_label_question = RemoteMultiLabelQuestion.from_api(payload)
    assert multi_label_question.type == QuestionTypes.multi_label_selection
    assert multi_label_question.server_settings == payload.settings
    assert multi_label_question.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "values": ["a", "b", "c"]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "ranking",
                    "options": [{"text": "a", "value": "a"}, {"text": "b", "value": "b"}, {"text": "c", "value": "c"}],
                },
            },
        ),
        (
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "values": {"a": "A", "b": "B", "c": "C"},
            },
            {
                "name": "a",
                "title": "B",
                "description": "b",
                "required": False,
                "settings": {
                    "type": "ranking",
                    "options": [{"text": "A", "value": "a"}, {"text": "B", "value": "b"}, {"text": "C", "value": "c"}],
                },
            },
        ),
    ],
)
def test_remote_ranking_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    ranking_question = RemoteRankingQuestion(**schema_kwargs)
    assert ranking_question.type == QuestionTypes.ranking
    assert ranking_question.server_settings == server_payload["settings"]
    assert ranking_question.to_server_payload() == server_payload

    local_ranking_question = ranking_question.to_local()
    assert isinstance(local_ranking_question, RankingQuestion)
    assert local_ranking_question.type == QuestionTypes.ranking
    assert local_ranking_question.server_settings == server_payload["settings"]
    assert local_ranking_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackQuestionModel(
            id=uuid4(),
            name="a",
            title="A",
            description="Description",
            required=True,
            settings={
                "type": "ranking",
                "options": [{"text": "a", "value": "a"}, {"text": "b", "value": "b"}, {"text": "c", "value": "c"}],
            },
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackQuestionModel(
            id=uuid4(),
            name="b",
            title="B",
            description="Description",
            required=False,
            settings={
                "type": "ranking",
                "options": [{"text": "A", "value": "a"}, {"text": "B", "value": "b"}, {"text": "C", "value": "c"}],
            },
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_ranking_question_from_api(payload: FeedbackQuestionModel) -> None:
    ranking_question = RemoteRankingQuestion.from_api(payload)
    assert ranking_question.type == QuestionTypes.ranking
    assert ranking_question.server_settings == payload.settings
    assert ranking_question.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


def test_span_questions_from_api():
    model = FeedbackQuestionModel(
        id=uuid4(),
        name="question",
        title="Question",
        required=True,
        settings={
            "type": "span",
            "field": "field",
            "visible_options": None,
            "allow_overlapping": False,
            "options": [
                {"text": "Span label a", "value": "a", "description": None},
                {
                    "text": "Span label b",
                    "value": "b",
                    "description": None,
                },
            ],
        },
        inserted_at=datetime.now(),
        updated_at=datetime.now(),
    )
    question = RemoteSpanQuestion.from_api(model)

    assert question.type == QuestionTypes.span
    assert question.server_settings == model.settings
    assert question.to_server_payload() == model.dict(exclude={"id", "inserted_at", "updated_at"})
    assert question.to_local().type == QuestionTypes.span


def test_span_questions_from_api_with_visible_labels():
    model = FeedbackQuestionModel(
        id=uuid4(),
        name="question",
        title="Question",
        required=True,
        settings={
            "type": "span",
            "field": "field",
            "visible_options": 3,
            "allow_overlapping": False,
            "options": [
                {"text": "Span label a", "value": "a", "description": None},
                {"text": "Span label b", "value": "b", "description": None},
                {"text": "Span label c", "value": "c", "description": None},
                {"text": "Span label d", "value": "d", "description": None},
            ],
        },
        inserted_at=datetime.now(),
        updated_at=datetime.now(),
    )
    question = RemoteSpanQuestion.from_api(model)

    assert question.type == QuestionTypes.span
    assert question.server_settings == model.settings
    assert question.to_server_payload() == model.dict(exclude={"id", "inserted_at", "updated_at"})
    assert question.to_local().type == QuestionTypes.span
