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

import tempfile
from typing import TYPE_CHECKING, List

import datasets
import pytest
from argilla.client import api

if TYPE_CHECKING:
    from argilla.client.feedback.schemas import AllowedFieldTypes, AllowedQuestionTypes

from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas import (
    FeedbackDatasetConfig,
    FeedbackRecord,
    RatingQuestion,
    TextField,
    TextQuestion,
)


@pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_fields", "feedback_dataset_questions")
def test_init(
    feedback_dataset_guidelines: str, feedback_dataset_fields: list, feedback_dataset_questions: list
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )

    assert dataset.guidelines == feedback_dataset_guidelines
    assert dataset.fields == feedback_dataset_fields
    assert dataset.questions == feedback_dataset_questions


@pytest.mark.usefixtures("feedback_dataset_fields", "feedback_dataset_questions")
def test_init_wrong_guidelines(feedback_dataset_fields: list, feedback_dataset_questions: list) -> None:
    with pytest.raises(TypeError, match="Expected `guidelines` to be"):
        FeedbackDataset(
            guidelines=[],
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="Expected `guidelines` to be"):
        FeedbackDataset(
            guidelines="",
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )


@pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_questions")
def test_init_wrong_fields(feedback_dataset_guidelines: str, feedback_dataset_questions: list) -> None:
    with pytest.raises(TypeError, match="Expected `fields` to be a list"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=None,
            questions=feedback_dataset_questions,
        )
    with pytest.raises(TypeError, match="Expected `fields` to be a list of `FieldSchema`"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[{"wrong": "field"}],
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="At least one `FieldSchema` in `fields` must be required"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[TextField(name="test", required=False)],
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="Expected `fields` to have unique names"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[
                TextField(name="test", required=True),
                TextField(name="test", required=True),
            ],
            questions=feedback_dataset_questions,
        )


@pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_fields")
def test_init_wrong_questions(feedback_dataset_guidelines: str, feedback_dataset_fields: list) -> None:
    with pytest.raises(TypeError, match="Expected `questions` to be a list, got"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=None,
        )
    with pytest.raises(
        TypeError,
        match="Expected `questions` to be a list of `TextQuestion`, `RatingQuestion`, `LabelQuestion`, and/or `MultiLabelQuestion`",
    ):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[{"wrong": "question"}],
        )
    with pytest.raises(ValueError, match="At least one question in `questions` must be required"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[
                TextQuestion(name="question-1", required=False),
                RatingQuestion(name="question-2", values=[0, 1], required=False),
            ],
        )
    with pytest.raises(ValueError, match="Expected `questions` to have unique names"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[
                TextQuestion(name="question-1", required=True),
                TextQuestion(name="question-1", required=True),
            ],
        )


@pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_fields", "feedback_dataset_questions")
def test_records(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )

    assert dataset.records == []

    dataset.add_records(
        [
            FeedbackRecord(
                fields={
                    "text": "A",
                    "label": "B",
                },
            ),
        ]
    )

    assert len(dataset.records) == 1
    assert dataset.records[0].fields == {
        "text": "A",
        "label": "B",
    }
    assert dataset.records[0].responses == []

    dataset.add_records(
        [
            FeedbackRecord(
                fields={
                    "text": "C",
                    "label": "D",
                },
                responses={
                    "values": {
                        "question-1": {"value": "answer"},
                        "question-2": {"value": 0},
                        "question-3": {"value": "a"},
                        "question-4": {"value": ["a", "b"]},
                    },
                    "status": "submitted",
                },
                external_id="test-id",
            ),
        ]
    )

    assert len(dataset.records) == 2
    assert dataset.records[1].fields == {
        "text": "C",
        "label": "D",
    }
    assert dataset.records[1].responses[0].dict() == {
        "user_id": None,
        "values": {
            "question-1": {"value": "answer"},
            "question-2": {"value": 0},
            "question-3": {"value": "a"},
            "question-4": {"value": ["a", "b"]},
        },
        "status": "submitted",
    }

    with pytest.raises(ValueError, match="Expected `records` to be a non-empty list"):
        dataset.add_records([])

    with pytest.raises(ValueError, match="Expected `records` to be a list of `dict` or `rg.FeedbackRecord`"):
        dataset.add_records([None])

    with pytest.raises(ValueError, match="Expected `records` to be a `dict` or `rg.FeedbackRecord`"):
        dataset.add_records(None)

    with pytest.raises(ValueError, match="`rg.FeedbackRecord.fields` does not match the expected schema"):
        dataset.add_records(
            [
                FeedbackRecord(
                    fields={
                        "wrong": "field",
                    },
                ),
            ]
        )

    for record in dataset.records:
        assert isinstance(record, FeedbackRecord)

    for batch in dataset.iter(batch_size=1):
        assert len(batch) == 1
        for record in batch:
            assert isinstance(record, FeedbackRecord)

    assert len(dataset[:2]) == 2
    assert len(dataset[1:2]) == 1
    assert len(dataset) == len(dataset.records)


@pytest.mark.parametrize("format_as,expected_output", [("datasets", datasets.Dataset)])
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines", "feedback_dataset_fields", "feedback_dataset_questions", "feedback_dataset_records"
)
def test_format_as(
    mocked_client,
    format_as,
    expected_output,
    feedback_dataset_guidelines,
    feedback_dataset_fields,
    feedback_dataset_questions,
    feedback_dataset_records,
) -> None:
    api.active_api()
    api.init(api_key="argilla.apikey")

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records)

    ds = dataset.format_as(format=format_as)
    assert isinstance(ds, expected_output)


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_push_to_argilla_and_from_argilla(
    mocked_client,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    api.active_api()
    api.init(api_key="argilla.apikey")

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records)
    dataset.push_to_argilla(name="test-dataset")

    assert dataset.argilla_id is not None

    dataset.add_records(
        [
            FeedbackRecord(
                fields={
                    "text": "E",
                    "label": "F",
                },
                responses=[
                    {
                        "values": {
                            "question-1": {"value": "answer"},
                            "question-2": {"value": 0},
                            "question-3": {"value": "a"},
                            "question-4": {"value": ["a", "b"]},
                        },
                        "status": "submitted",
                    },
                    {
                        "values": {
                            "question-1": {"value": "answer"},
                            "question-2": {"value": 0},
                            "question-3": {"value": "a"},
                            "question-4": {"value": ["a", "b"]},
                        },
                        "status": "submitted",
                    },
                ],
            ),
        ]
    )

    with pytest.warns(UserWarning, match="Multiple responses without `user_id`"):
        dataset.push_to_argilla()

    dataset_from_argilla = FeedbackDataset.from_argilla(id=dataset.argilla_id)

    assert dataset_from_argilla.guidelines == dataset.guidelines
    assert len(dataset_from_argilla.fields) == len(dataset.fields)
    assert [field.name for field in dataset_from_argilla.fields] == [field.name for field in dataset.fields]
    assert len(dataset_from_argilla.questions) == len(dataset.questions)
    assert [question.name for question in dataset_from_argilla.questions] == [
        question.name for question in dataset.questions
    ]
    assert len(dataset_from_argilla.records) == len(dataset.records)
    assert len(dataset_from_argilla.records[-1].responses) == 1  # Since the second one was discarded as `user_id=None`


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_push_to_huggingface_and_from_huggingface(
    mocked_client,
    monkeypatch,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    api.active_api()
    api.init(api_key="argilla.apikey")

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records)

    monkeypatch.setattr("datasets.arrow_dataset.Dataset.push_to_hub", lambda *args, **kwargs: None)
    monkeypatch.setattr("huggingface_hub.hf_api.HfApi.upload_file", lambda *args, **kwargs: None)
    monkeypatch.setattr("huggingface_hub.repocard.RepoCard.push_to_hub", lambda *args, **kwargs: None)

    dataset.push_to_huggingface(repo_id="test-dataset", generate_card=True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
        f.write(
            FeedbackDatasetConfig(
                fields=feedback_dataset_fields,
                questions=feedback_dataset_questions,
                guidelines=feedback_dataset_guidelines,
            ).json()
        )
        config_file = f.name

    monkeypatch.setattr("huggingface_hub.file_download.hf_hub_download", lambda *args, **kwargs: config_file)
    monkeypatch.setattr("datasets.load_dataset", lambda *args, **kwargs: dataset.format_as("datasets"))

    dataset_from_huggingface = FeedbackDataset.from_huggingface(repo_id="test-dataset")
    assert isinstance(dataset_from_huggingface, FeedbackDataset)
    assert dataset_from_huggingface.guidelines == dataset.guidelines
    assert len(dataset_from_huggingface.fields) == len(dataset.fields)
    assert all(original_field in dataset_from_huggingface.fields for original_field in dataset.fields)
    assert len(dataset_from_huggingface.questions) == len(dataset.questions)
    assert all(original_question in dataset_from_huggingface.questions for original_question in dataset.questions)
