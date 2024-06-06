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

from typing import Any, Dict

import pytest
from argilla_v1.client.feedback.schemas.enums import LabelsOrder, QuestionTypes
from argilla_v1.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    SpanLabelOption,
    SpanQuestion,
    TextQuestion,
    _LabelQuestion,
)

from tests.pydantic_v1 import ValidationError


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
def test_text_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    text_question = TextQuestion(**schema_kwargs)
    assert text_question.type == QuestionTypes.text
    assert text_question.server_settings == server_payload["settings"]
    assert text_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "values": [8, 9, 10]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {"type": "rating", "options": [{"value": 8}, {"value": 9}, {"value": 10}]},
            },
        ),
        (
            {"name": "a", "title": "A", "description": "a", "required": False, "values": [0, 1, 2, 3]},
            {
                "name": "a",
                "title": "A",
                "description": "a",
                "required": False,
                "settings": {"type": "rating", "options": [{"value": 0}, {"value": 1}, {"value": 2}, {"value": 3}]},
            },
        ),
    ],
)
def test_rating_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    rating_question = RatingQuestion(**schema_kwargs)
    assert rating_question.type == QuestionTypes.rating
    assert rating_question.server_settings == server_payload["settings"]
    assert rating_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a", "values": ["a", "b"]}, ValidationError, "value is not a valid integer"),
        ({"name": "a", "values": [1, 1, 1]}, ValidationError, "the list has duplicated items"),
        ({"name": "a", "values": [1]}, ValidationError, "ensure this value has at least 2 items"),
        ({"name": "a", "values": [-1, 0, 1]}, ValidationError, "ensure this value is greater than or equal to 0"),
        ({"name": "a", "values": [1, 11]}, ValidationError, "ensure this value is less than or equal to 10"),
    ],
)
def test_rating_question_errors(schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        RatingQuestion(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a", "labels": ["a"]}, ValidationError, "ensure this value has at least 2 items"),
        (
            {"name": "a", "labels": ["a", "b"], "visible_labels": 2},
            ValidationError,
            "ensure this value is greater than or equal to 3",
        ),
        ({"name": "a", "labels": ["a", "a"]}, ValidationError, "the list has duplicated items"),
        ({"name": "a", "labels": "a"}, ValidationError, r"(value is not a valid list)|(value is not a valid dict)"),
        ({"name": "a", "labels": {"a": "a"}}, ValidationError, "ensure this dict has at least 2 items"),
        ({"name": "a", "labels": {"a": "a", "b": "a"}}, ValidationError, "ensure this dict has unique values"),
    ],
)
def test_label_question_errors(schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        _LabelQuestion(**schema_kwargs, type="label_selection")


@pytest.mark.parametrize(
    "schema_kwargs, warning_cls, warning_message",
    [
        (
            {"name": "a", "labels": ["a", "b", "c"], "visible_labels": 4},
            UserWarning,
            "\`visible_labels=4\` is greater than the total number of labels \(3\), so it will be set to \`3\`.",
        ),
        (
            {"name": "a", "labels": ["a", "b"], "visible_labels": 3},
            UserWarning,
            "\`labels=\['a', 'b'\]\` has less than 3 labels, so \`visible_labels\` will be set to \`None\`, which means that all the labels will be visible.",
        ),
        (
            {"name": "a", "labels": list(range(100))},
            UserWarning,
            "Since \`visible_labels\` has not been provided and the total number of labels is greater than 20, \`visible_labels\` will be set to \`20\`.",
        ),
    ],
)
def test_label_question_warnings(schema_kwargs: Dict[str, Any], warning_cls: Warning, warning_message: str) -> None:
    with pytest.warns(warning_cls, match=warning_message):
        _LabelQuestion(**schema_kwargs, type="label_selection")


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "labels": ["a", "b"]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                    "visible_options": None,
                },
            },
        ),
        (
            {"name": "a", "labels": {"a": "A", "b": "B"}},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": "a", "text": "A"}, {"value": "b", "text": "B"}],
                    "visible_options": None,
                },
            },
        ),
        (
            {"name": "a", "labels": ["a", "b"], "visible_labels": 3},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                    "visible_options": None,
                },
            },
        ),
        (
            {"name": "a", "labels": ["a", "b"], "visible_labels": None},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                    "visible_options": None,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(20))},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(20))],
                    "visible_options": None,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(21))},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(21))],
                    "visible_options": 20,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(2)), "visible_labels": None},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(2))],
                    "visible_options": None,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(2)), "visible_labels": 3},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(2))],
                    "visible_options": None,
                },
            },
        ),
    ],
)
def test_label_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    label_question = LabelQuestion(**schema_kwargs)
    assert label_question.type == QuestionTypes.label_selection
    assert label_question.server_settings == server_payload["settings"]
    assert label_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "labels": ["a", "b"]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                    "visible_options": None,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
        (
            {"name": "a", "labels": {"a": "A", "b": "B"}, "labels_order": LabelsOrder.suggestion},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": "a", "text": "A"}, {"value": "b", "text": "B"}],
                    "visible_options": None,
                    "options_order": LabelsOrder.suggestion,
                },
            },
        ),
        (
            {"name": "a", "labels": ["a", "b"], "visible_labels": 3},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                    "visible_options": None,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
        (
            {"name": "a", "labels": ["a", "b"], "visible_labels": None},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                    "visible_options": None,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(20))},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(20))],
                    "visible_options": None,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(21))},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(21))],
                    "visible_options": 20,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(2)), "visible_labels": None},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(2))],
                    "visible_options": None,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
        (
            {"name": "a", "labels": list(range(2)), "visible_labels": 3},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": str(n), "text": str(n)} for n in list(range(2))],
                    "visible_options": None,
                    "options_order": LabelsOrder.natural,
                },
            },
        ),
    ],
)
def test_multi_label_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    label_question = MultiLabelQuestion(**schema_kwargs)
    assert label_question.type == QuestionTypes.multi_label_selection
    assert label_question.server_settings == server_payload["settings"]
    assert label_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "values": ["a", "b"]},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {"type": "ranking", "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}]},
            },
        ),
        (
            {"name": "a", "values": {"a": "A", "b": "B"}},
            {
                "name": "a",
                "title": "A",
                "description": None,
                "required": True,
                "settings": {"type": "ranking", "options": [{"value": "a", "text": "A"}, {"value": "b", "text": "B"}]},
            },
        ),
    ],
)
def test_ranking_question(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    ranking_question = RankingQuestion(**schema_kwargs)
    assert ranking_question.type == QuestionTypes.ranking
    assert ranking_question.server_settings == server_payload["settings"]
    assert ranking_question.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a", "values": [1, 1]}, ValidationError, "the list has duplicated items"),
        ({"name": "a", "values": ["a"]}, ValidationError, "ensure this value has at least 2 items"),
        ({"name": "a", "values": {"a": "a"}}, ValidationError, "ensure this dict has at least 2 items"),
        ({"name": "a", "values": {1: "a", 2: "a"}}, ValidationError, "ensure this dict has unique values"),
    ],
)
def test_ranking_question_errors(schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        RankingQuestion(**schema_kwargs)


def test_span_question() -> None:
    question = SpanQuestion(
        name="question",
        field="field",
        title="Question",
        description="Description",
        required=True,
        allow_overlapping=True,
        labels=["a", "b"],
    )

    assert question.type == QuestionTypes.span
    assert question.server_settings == {
        "type": "span",
        "field": "field",
        "visible_options": None,
        "allow_overlapping": True,
        "options": [{"value": "a", "text": "a", "description": None}, {"value": "b", "text": "b", "description": None}],
    }


def test_span_question_with_labels_dict() -> None:
    question = SpanQuestion(
        name="question",
        field="field",
        title="Question",
        description="Description",
        labels={"a": "A text", "b": "B text"},
    )

    assert question.type == QuestionTypes.span
    assert question.server_settings == {
        "type": "span",
        "field": "field",
        "visible_options": None,
        "allow_overlapping": False,
        "options": [
            {"value": "a", "text": "A text", "description": None},
            {"value": "b", "text": "B text", "description": None},
        ],
    }


def test_span_question_with_visible_labels() -> None:
    question = SpanQuestion(
        name="question",
        field="field",
        title="Question",
        description="Description",
        labels=["a", "b", "c", "d"],
        visible_labels=3,
    )

    assert question.type == QuestionTypes.span
    assert question.server_settings == {
        "type": "span",
        "field": "field",
        "visible_options": 3,
        "allow_overlapping": False,
        "options": [
            {"value": "a", "text": "a", "description": None},
            {"value": "b", "text": "b", "description": None},
            {"value": "c", "text": "c", "description": None},
            {"value": "d", "text": "d", "description": None},
        ],
    }


def test_span_question_with_visible_labels_default_value():
    question = SpanQuestion(
        name="question",
        field="field",
        title="Question",
        description="Description",
        labels=list(range(21)),
    )

    assert question.visible_labels == 20


def test_span_question_with_default_visible_label_when_labels_is_less_than_20():
    with pytest.warns(UserWarning, match=""):
        question = SpanQuestion(
            name="question",
            field="field",
            title="Question",
            description="Description",
            labels=list(range(19)),
        )

        assert question.visible_labels == 19


def test_span_question_when_visible_labels_is_greater_than_total_labels():
    with pytest.warns(
        UserWarning,
        match="`visible_labels=4` is greater than the total number of labels \(3\)",
    ):
        question = SpanQuestion(
            name="question",
            field="field",
            title="Question",
            description="Description",
            labels=["a", "b", "c"],
            visible_labels=4,
        )

        assert question.visible_labels == 3


def test_span_question_with_visible_labels_less_than_total_labels():
    with pytest.warns(
        UserWarning, match="Since `labels` has less than 3 labels, `visible_labels` will be set to `None`."
    ):
        question = SpanQuestion(
            name="question",
            field="field",
            title="Question",
            description="Description",
            labels=["a", "b"],
            visible_labels=3,
        )

        assert question.visible_labels is None


def test_span_question_with_visible_labels_less_than_min_value():
    with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 3"):
        SpanQuestion(
            name="question",
            field="field",
            title="Question",
            description="Description",
            labels=["a", "b"],
            visible_labels=2,
        )


def test_span_questions_with_default_visible_labels_and_less_labels_than_default():
    with pytest.warns(UserWarning, match="visible_labels=20` is greater than the total number of labels"):
        question = SpanQuestion(
            name="question",
            field="field",
            title="Question",
            description="Description",
            labels=list(range(10)),
        )

        assert question.visible_labels == 10


def test_span_question_with_no_labels() -> None:
    with pytest.raises(ValidationError, match="At least one label must be provided"):
        SpanQuestion(
            name="question",
            field="field",
            title="Question",
            description="Description",
            labels=[],
        )


def test_span_question_with_duplicated_labels() -> None:
    with pytest.raises(ValidationError, match="the list has duplicated items"):
        SpanQuestion(
            name="question",
            title="Question",
            field="field",
            description="Description",
            labels=[SpanLabelOption(value="a", text="A text"), SpanLabelOption(value="a", text="Text for A")],
        )
