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
from typing import TYPE_CHECKING, List, Type, Union

import datasets
import pytest
from argilla.client import api
from argilla.client.feedback.config import DatasetConfig
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla.client.feedback.schemas.remote.records import RemoteSuggestionSchema
from argilla.client.feedback.training.schemas import TrainingTask
from argilla.client.models import Framework

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.server.models import User as ServerUser
    from sqlalchemy.ext.asyncio import AsyncSession

    from tests.integration.helpers import SecuredClient


def test_init(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )

    assert dataset.guidelines == feedback_dataset_guidelines
    assert dataset.fields == feedback_dataset_fields
    assert dataset.questions == feedback_dataset_questions


def test_init_wrong_guidelines(
    feedback_dataset_fields: List["AllowedFieldTypes"], feedback_dataset_questions: List["AllowedQuestionTypes"]
) -> None:
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


def test_init_wrong_fields(
    feedback_dataset_guidelines: str, feedback_dataset_questions: List["AllowedQuestionTypes"]
) -> None:
    with pytest.raises(TypeError, match="Expected `fields` to be a list"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=None,
            questions=feedback_dataset_questions,
        )
    with pytest.raises(TypeError, match="Expected `fields` to be a list of `TextField`"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[{"wrong": "field"}],
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="At least one field in `fields` must be required"):
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


def test_init_wrong_questions(
    feedback_dataset_guidelines: str, feedback_dataset_fields: List["AllowedFieldTypes"]
) -> None:
    with pytest.raises(TypeError, match="Expected `questions` to be a list, got"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=None,
        )
    with pytest.raises(
        TypeError,
        match="Expected `questions` to be a list of",
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
                RatingQuestion(name="question-2", values=[1, 2], required=False),
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


def test_create_dataset_with_suggestions(argilla_user: "ServerUser") -> None:
    api.init(api_key=argilla_user.api_key)

    ds = FeedbackDataset(fields=[TextField(name="text")], questions=[TextQuestion(name="text")])

    ds.add_records(
        records=[
            FeedbackRecord(
                fields={"text": "this is a text"},
                suggestions=[{"question_name": "text", "value": "This is a suggestion"}],
            )
        ]
    )

    remote_dataset = ds.push_to_argilla(name="new_dataset")

    assert len(remote_dataset.records) == 1
    assert remote_dataset.records[0].id is not None
    assert isinstance(remote_dataset.records[0].suggestions[0], RemoteSuggestionSchema)
    assert remote_dataset.records[0].suggestions[0].question_id == remote_dataset.question_by_name("text").id


@pytest.mark.asyncio
async def test_update_dataset_records_with_suggestions(argilla_user: "ServerUser", db: "AsyncSession"):
    api.init(api_key=argilla_user.api_key)

    ds = FeedbackDataset(fields=[TextField(name="text")], questions=[TextQuestion(name="text")])

    ds.add_records(records=[FeedbackRecord(fields={"text": "this is a text"})])

    remote_dataset = ds.push_to_argilla(name="new_dataset", workspace="argilla")

    assert len(remote_dataset.records) == 1
    assert remote_dataset.records[0].id is not None
    assert remote_dataset.records[0].suggestions == ()

    remote_dataset.records[0].update(suggestions=[{"question_name": "text", "value": "This is a suggestion"}])

    # TODO: Review this requirement for tests and explain, try to avoid use or at least, document.
    await db.refresh(argilla_user, attribute_names=["datasets"])
    dataset = argilla_user.datasets[0]
    await db.refresh(dataset, attribute_names=["records"])
    record = dataset.records[0]
    await db.refresh(record, attribute_names=["suggestions"])

    for record in remote_dataset.records:
        assert record.suggestions[0].question_id == remote_dataset.question_by_name("text").id


def test_add_records(
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
    assert not dataset.records[0].metadata
    assert not dataset.records[0].responses
    assert not dataset.records[0].suggestions

    dataset.add_records(
        [
            FeedbackRecord(
                fields={
                    "text": "C",
                    "label": "D",
                },
                metadata={"unit": "test"},
                responses=[
                    {
                        "values": {
                            "question-1": {"value": "answer"},
                            "question-2": {"value": 0},
                            "question-3": {"value": "a"},
                            "question-4": {"value": ["a", "b"]},
                            "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                        },
                        "status": "submitted",
                    },
                ],
                suggestions=[
                    {
                        "question_name": "question-1",
                        "value": "answer",
                    },
                    {
                        "question_name": "question-2",
                        "value": 0,
                    },
                    {
                        "question_name": "question-3",
                        "value": "a",
                    },
                    {
                        "question_name": "question-4",
                        "value": ["a", "b"],
                    },
                    {
                        "question_name": "question-5",
                        "value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}],
                    },
                ],
                external_id="test-id",
            ),
        ]
    )

    assert len(dataset.records) == 2
    assert dataset.records[1].fields == {
        "text": "C",
        "label": "D",
    }
    assert dataset.records[1].metadata == {"unit": "test"}
    assert dataset.records[1].responses[0].dict() == {
        "user_id": None,
        "values": {
            "question-1": {"value": "answer"},
            "question-2": {"value": 0},
            "question-3": {"value": "a"},
            "question-4": {"value": ["a", "b"]},
            "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
        },
        "status": "submitted",
    }
    assert dataset.records[1].suggestions[0].dict() == {
        "question_name": "question-1",
        "value": "answer",
        "type": None,
        "score": None,
        "agent": None,
    }

    with pytest.raises(ValueError, match="Expected `records` to be a non-empty list"):
        dataset.add_records([])

    with pytest.raises(ValueError, match="Expected `records` to be a list of `dict` or `FeedbackRecord`"):
        dataset.add_records([None])

    with pytest.raises(ValueError, match="`FeedbackRecord.fields` does not match the expected schema"):
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
def test_format_as(
    mocked_client: "SecuredClient",
    format_as: str,
    expected_output: Type[datasets.Dataset],
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

    ds = dataset.format_as(format=format_as)
    assert isinstance(ds, expected_output)


@pytest.mark.asyncio
async def test_push_to_argilla_and_from_argilla(
    mocked_client: "SecuredClient",
    argilla_user: "ServerUser",
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    db: "AsyncSession",
) -> None:
    api.active_api()
    api.init(api_key=argilla_user.api_key)

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    # Make sure UUID in `user_id` is pushed to Argilla with no issues as it should be
    # converted to a string
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
                            "question-2": {"value": 1},
                            "question-3": {"value": "a"},
                            "question-4": {"value": ["a", "b"]},
                            "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                        },
                        "status": "submitted",
                    },
                    {
                        "values": {
                            "question-1": {"value": "answer"},
                            "question-2": {"value": 1},
                            "question-3": {"value": "a"},
                            "question-4": {"value": ["a", "b"]},
                            "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                        },
                        "status": "submitted",
                    },
                ],
            ),
        ]
    )

    with pytest.warns(UserWarning, match="Multiple responses without `user_id`"):
        remote_dataset = dataset.push_to_argilla(name="my-dataset")

    dataset_from_argilla = FeedbackDataset.from_argilla(id=remote_dataset.id)

    assert dataset_from_argilla.guidelines == dataset.guidelines
    assert len(dataset_from_argilla.fields) == len(dataset.fields)
    assert len(dataset_from_argilla.questions) == len(dataset.questions)
    assert len(dataset_from_argilla.records) == len(dataset.records)
    assert len(dataset_from_argilla.records[-1].responses) == 1  # Since the second one was discarded as `user_id=None`


@pytest.mark.asyncio
async def test_copy_dataset_in_argilla(
    mocked_client: "SecuredClient",
    argilla_user: "ServerUser",
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
    db: "AsyncSession",
) -> None:
    api.active_api()
    api.init(api_key=argilla_user.api_key)

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records)
    dataset.push_to_argilla(name="test-dataset")

    await db.refresh(argilla_user, attribute_names=["datasets"])

    same_dataset = FeedbackDataset.from_argilla("test-dataset")
    same_dataset_local = same_dataset.pull()
    same_dataset_local.push_to_argilla("copy-dataset")
    assert same_dataset.id is not None

    await db.refresh(argilla_user, attribute_names=["datasets"])

    same_dataset_copy = FeedbackDataset.from_argilla("copy-dataset")
    assert same_dataset_copy.id != same_dataset.id
    assert [field.to_local() for field in same_dataset_copy.fields] == [
        field.to_local() for field in same_dataset.fields
    ]
    assert [question.to_local() for question in same_dataset_copy.questions] == [
        question.to_local() for question in same_dataset.questions
    ]


@pytest.mark.asyncio
async def test_update_dataset_records_in_argilla(
    mocked_client: "SecuredClient",
    argilla_user: "ServerUser",
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
    db: "AsyncSession",
) -> None:
    api.active_api()
    api.init(api_key=argilla_user.api_key)

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records)
    remote_dataset = dataset.push_to_argilla(name="test-dataset")
    await db.refresh(argilla_user, attribute_names=["datasets"])

    for record in remote_dataset.records:
        record.update(
            suggestions=[
                {
                    "question_name": "question-1",
                    "value": "This is a suggestion to question 1",
                },
            ]
        )

    await db.refresh(argilla_user, attribute_names=["datasets"])

    remote_dataset = FeedbackDataset.from_argilla("test-dataset")
    for record in remote_dataset.records:
        record.update(
            suggestions=[
                {
                    "question_name": "question-1",
                    "value": "This is a suggestion to question 1",
                },
            ]
        )

    await db.refresh(argilla_user, attribute_names=["datasets"])

    for record in remote_dataset.records:
        record.update(
            suggestions=[
                {
                    "question_name": "question-2",
                    "value": 1,
                },
            ]
        )

    new_remote_dataset = dataset.push_to_argilla("new-test-dataset")
    await db.refresh(argilla_user, attribute_names=["datasets"])

    record = new_remote_dataset.records[0]
    with pytest.warns(UserWarning, match="A suggestion for question `question-1`"):
        record.update(
            suggestions=[
                {
                    "question_name": "question-1",
                    "value": "This is a suggestion to question 1",
                },
                {
                    "question_name": "question-1",
                    "value": "This is a suggestion to question 1",
                },
            ]
        )
    with pytest.raises(TypeError, match='"RemoteFeedbackRecord" is immutable and does not support item assignment'):
        record.suggestions = [
            {
                "question_name": "question-1",
                "value": "This is a suggestion to question 1",
            },
        ]


def test_push_to_huggingface_and_from_huggingface(
    mocked_client: "SecuredClient",
    monkeypatch: pytest.MonkeyPatch,
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

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(
            DatasetConfig(
                fields=feedback_dataset_fields,
                questions=feedback_dataset_questions,
                guidelines=feedback_dataset_guidelines,
            ).to_yaml()
        )
        config_file = f.name

    monkeypatch.setattr("huggingface_hub.hf_hub_download", lambda *args, **kwargs: config_file)
    monkeypatch.setattr("datasets.load_dataset", lambda *args, **kwargs: dataset.format_as("datasets"))

    dataset_from_huggingface = FeedbackDataset.from_huggingface(repo_id="test-dataset")
    assert isinstance(dataset_from_huggingface, FeedbackDataset)
    assert dataset_from_huggingface.guidelines == dataset.guidelines
    assert len(dataset_from_huggingface.fields) == len(dataset.fields)
    assert all(original_field in dataset_from_huggingface.fields for original_field in dataset.fields)
    assert len(dataset_from_huggingface.questions) == len(dataset.questions)
    assert all(original_question in dataset_from_huggingface.questions for original_question in dataset.questions)

    for hf_record, record in zip(dataset_from_huggingface.records, dataset.records):
        assert hf_record.fields == record.fields
        assert hf_record.metadata == record.metadata
        assert len(hf_record.responses) == len(record.responses)
        assert all(
            hf_response.dict() == response.dict()
            for hf_response, response in zip(hf_record.responses, record.responses)
        )

    dataset.add_records(
        records=[
            FeedbackRecord(
                fields={"text": "This is a negative example", "label": "negative"},
                responses=[
                    {
                        "values": {
                            "question-1": {"value": "This is a response to question 1"},
                            "question-2": {"value": 0},
                            "question-3": {"value": "b"},
                            "question-4": {"value": ["b", "c"]},
                            "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                        },
                        "status": "submitted",
                    },
                    {
                        "values": {
                            "question-1": {"value": "This is a response to question 1"},
                            "question-2": {"value": 0},
                            "question-3": {"value": "b"},
                            "question-4": {"value": ["b", "c"]},
                            "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                        },
                        "status": "submitted",
                    },
                ],
            ),
        ],
    )

    monkeypatch.setattr("datasets.arrow_dataset.Dataset.push_to_hub", lambda *args, **kwargs: None)
    monkeypatch.setattr("huggingface_hub.hf_api.HfApi.upload_file", lambda *args, **kwargs: None)
    monkeypatch.setattr("huggingface_hub.repocard.RepoCard.push_to_hub", lambda *args, **kwargs: None)

    dataset.push_to_huggingface(repo_id="test-dataset", generate_card=True)

    monkeypatch.setattr("huggingface_hub.hf_hub_download", lambda *args, **kwargs: config_file)
    monkeypatch.setattr("datasets.load_dataset", lambda *args, **kwargs: dataset.format_as("datasets"))

    with pytest.warns(UserWarning, match="Found more than one user without ID"):
        dataset_from_huggingface = FeedbackDataset.from_huggingface(repo_id="test-dataset")


@pytest.mark.parametrize(
    "framework",
    [
        Framework("spacy"),
        Framework("transformers"),
        Framework("spark-nlp"),
        Framework("openai"),
        Framework("spacy-transformers"),
    ],
)
@pytest.mark.parametrize(
    "question",
    ["question-3", "question-4"],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_text_classification(
    framework: Union[Framework, str],
    question: str,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(feedback_dataset_records)
    label = dataset.question_by_name(question)
    task = TrainingTask.for_text_classification(text=dataset.fields[0], label=label)

    dataset.prepare_for_training(framework=framework, task=task)


def test_for_extractive_question_answering():
    dataset = FeedbackDataset.for_extractive_question_answering(use_markdown=True)
    assert len(dataset.fields) == 2
    assert len(dataset.questions) == 1
    assert dataset.questions[0].name == "answer"
    assert (
        dataset.questions[0].description == "Answer the question. Note that the answer must exactly be in the context."
    )
    assert dataset.questions[0].required == True
    assert dataset.fields[0].name == "question"
    assert dataset.fields[0].use_markdown == True
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown == True
    assert (
        dataset.guidelines
        == "This is a question answering dataset that contains questions and contexts. Please answer the question by using the context."
    )


def test_for_text_classification():
    # Test case 1: Single label classification
    dataset = FeedbackDataset.for_text_classification(labels=["positive", "negative"])
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert (
        dataset.questions[0].description
        == "Classify the text by selecting the correct label from the given list of labels."
    )
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["positive", "negative"]
    assert dataset.fields[0].name == "text"
    assert dataset.fields[0].use_markdown == False
    assert (
        dataset.guidelines
        == "This is a text classification dataset that contains texts and labels. Given a set of texts and a predefined set of labels, the goal of text classification is to assign one or more labels to each text based on its content. Please classify the texts by selecting the correct label."
    )

    # Test case 2: Multi-label classification
    dataset = FeedbackDataset.for_text_classification(labels=["positive", "negative"], multi_label=True)
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert (
        dataset.questions[0].description
        == "Classify the text by selecting the correct label from the given list of labels."
    )
    assert isinstance(dataset.questions[0], MultiLabelQuestion)
    assert dataset.questions[0].labels == ["positive", "negative"]
    assert dataset.fields[0].name == "text"
    assert dataset.fields[0].use_markdown == False
    print(dataset.guidelines)
    assert (
        dataset.guidelines
        == "This is a text classification dataset that contains texts and labels. Given a set of texts and a predefined set of labels, the goal of text classification is to assign one or more labels to each text based on its content. Please classify the texts by selecting the correct labels."
    )


def test_for_summarization():
    dataset = FeedbackDataset.for_summarization(use_markdown=True)
    assert len(dataset) == 0
    assert dataset.questions[0].name == "summary"
    assert dataset.questions[0].description == "Write a summary of the text."
    assert isinstance(dataset.questions[0], TextQuestion)
    assert dataset.fields[0].name == "text"
    assert dataset.fields[0].use_markdown == True
    assert (
        dataset.guidelines
        == "This is a summarization dataset that contains texts. Please summarize the text in the text field."
    )


def test_for_supervised_fine_tuning():
    # Test case 1: context=False, use_markdown=False, guidelines=None
    dataset = FeedbackDataset.for_supervised_fine_tuning(context=False, use_markdown=False, guidelines=None)
    assert len(dataset) == 0
    assert dataset.questions[0].name == "response"
    assert dataset.questions[0].description == "Write the response to the instruction."
    assert isinstance(dataset.questions[0], TextQuestion)
    assert dataset.questions[0].use_markdown == False
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown == False
    assert (
        dataset.guidelines
        == "This is a supervised fine-tuning dataset that contains instructions. Please write the response to the instruction in the response field."
    )

    # Test case 2: context=True, use_markdown=True, guidelines="Custom guidelines"
    dataset = FeedbackDataset.for_supervised_fine_tuning(
        context=True, use_markdown=True, guidelines="Custom guidelines"
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "response"
    assert dataset.questions[0].description == "Write the response to the instruction."
    assert isinstance(dataset.questions[0], TextQuestion)
    assert dataset.questions[0].use_markdown == True
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown == True
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown == True
    assert dataset.guidelines == "Custom guidelines"


def test_for_retrieval_augmented_generation():
    # Test case 1: Single document retrieval augmented generation
    dataset = FeedbackDataset.for_retrieval_augmented_generation(
        number_of_documents=1, rating_scale=5, use_markdown=True
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "question_rating_1"
    assert dataset.questions[0].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == [1, 2, 3, 4, 5]
    assert dataset.questions[1].name == "response"
    assert dataset.questions[1].description == "Write the response to the query."
    assert isinstance(dataset.questions[1], TextQuestion)
    assert dataset.fields[0].name == "query"
    assert dataset.fields[0].use_markdown == True
    assert dataset.fields[1].name == "retrieved_document_1"
    assert dataset.fields[1].use_markdown == True
    assert (
        dataset.guidelines
        == "This is a retrieval augmented generation dataset that contains queries and retrieved documents. Please rate the relevancy of retrieved document and write the response to the query in the response field."
    )

    # Test case 2: Multiple document retrieval augmented generation
    dataset = FeedbackDataset.for_retrieval_augmented_generation(
        number_of_documents=3, rating_scale=10, use_markdown=False, guidelines="Custom guidelines"
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "question_rating_1"
    assert dataset.questions[0].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == list(range(1, 11))
    assert dataset.questions[1].name == "question_rating_2"
    assert dataset.questions[1].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[1], RatingQuestion)
    assert dataset.questions[1].values == list(range(1, 11))
    assert dataset.questions[2].name == "question_rating_3"
    assert dataset.questions[2].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[2], RatingQuestion)
    assert dataset.questions[2].values == list(range(1, 11))
    assert dataset.questions[3].name == "response"
    assert dataset.questions[3].description == "Write the response to the query."
    assert isinstance(dataset.questions[3], TextQuestion)
    assert dataset.fields[0].name == "query"
    assert dataset.fields[0].use_markdown == False
    assert dataset.fields[1].name == "retrieved_document_1"
    assert dataset.fields[1].use_markdown == False
    assert dataset.fields[2].name == "retrieved_document_2"
    assert dataset.fields[2].use_markdown == False
    assert dataset.fields[3].name == "retrieved_document_3"
    assert dataset.fields[3].use_markdown == False
    assert dataset.guidelines == "Custom guidelines"


def test_for_sentence_similarity():
    # Test case 1: Default parameters
    dataset = FeedbackDataset.for_sentence_similarity()
    assert len(dataset) == 0
    assert dataset.questions[0].name == "similarity"
    assert dataset.questions[0].description == "Rate the similarity between the two sentences."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert dataset.fields[0].name == "sentence1"
    assert dataset.fields[0].use_markdown == False
    assert dataset.fields[1].name == "sentence2"
    assert dataset.fields[1].use_markdown == False
    assert (
        dataset.guidelines
        == "This is a sentence similarity dataset that contains two sentences. Please rate the similarity between the two sentences."
    )

    # Test case 2: Custom parameters
    dataset = FeedbackDataset.for_sentence_similarity(
        similarity_scale=5, use_markdown=True, guidelines="Custom guidelines"
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "similarity"
    assert dataset.questions[0].description == "Rate the similarity between the two sentences."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == [1, 2, 3, 4, 5]
    assert dataset.fields[0].name == "sentence1"
    assert dataset.fields[0].use_markdown == True
    assert dataset.fields[1].name == "sentence2"
    assert dataset.fields[1].use_markdown == True
    assert dataset.guidelines == "Custom guidelines"


def test_for_preference_modeling():
    dataset = FeedbackDataset.for_preference_modeling(use_markdown=False)
    assert len(dataset) == 0
    assert dataset.questions[0].name == "preference"
    assert dataset.questions[0].description == "Choose your preference."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["Response 1", "Response 2"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown == False
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown == False
    assert dataset.fields[1].required == False
    assert dataset.fields[2].name == "response1"
    assert dataset.fields[2].title == "Response 1"
    assert dataset.fields[2].use_markdown == False
    assert dataset.fields[3].name == "response2"
    assert dataset.fields[3].title == "Response 2"
    assert dataset.fields[3].use_markdown == False
    assert (
        dataset.guidelines
        == "This is a preference dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
    )


def test_for_natural_language_inference():
    # Test case 1: Default labels and guidelines
    dataset = FeedbackDataset.for_natural_language_inference()
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert dataset.questions[0].description == "Choose one of the labels."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["entailment", "neutral", "contradiction"]
    assert dataset.fields[0].name == "premise"
    assert dataset.fields[0].use_markdown == False
    assert dataset.fields[1].name == "hypothesis"
    assert dataset.fields[1].use_markdown == False
    assert (
        dataset.guidelines
        == "This is a natural language inference dataset that contains premises and hypotheses. Please choose the correct label for the given premise and hypothesis."
    )
    # Test case 2: Custom labels and guidelines
    dataset = FeedbackDataset.for_natural_language_inference(labels=["yes", "no"], guidelines="Custom guidelines")
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert dataset.questions[0].description == "Choose one of the labels."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["yes", "no"]
    assert dataset.fields[0].name == "premise"
    assert dataset.fields[0].use_markdown == False
    assert dataset.fields[1].name == "hypothesis"
    assert dataset.fields[1].use_markdown == False
    assert dataset.guidelines == "Custom guidelines"


def test_for_proximal_policy_optimization():
    # Test case 1: Without context and without markdown
    dataset = FeedbackDataset.for_proximal_policy_optimization()
    assert len(dataset) == 0
    assert dataset.questions[0].name == "prompt"
    assert dataset.questions[0].description == "Choose one of the labels that best describes the prompt."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["good", "bad"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown == False
    assert (
        dataset.guidelines
        == "This is a proximal policy optimization dataset that contains contexts and prompts. Please choose the label that best prompt."
    )

    # Test case 2: With context and with markdown
    dataset = FeedbackDataset.for_proximal_policy_optimization(context=True, use_markdown=True)
    assert len(dataset) == 0
    assert dataset.questions[0].name == "prompt"
    assert dataset.questions[0].description == "Choose one of the labels that best describes the prompt."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["good", "bad"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown == True
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown == True
    assert (
        dataset.guidelines
        == "This is a proximal policy optimization dataset that contains contexts and prompts. Please choose the label that best prompt."
    )


def test_for_direct_preference_optimization():
    # Test case 1: Without context and markdown
    dataset = FeedbackDataset.for_direct_preference_optimization()
    assert len(dataset) == 0
    assert dataset.questions[0].name == "preference"
    assert dataset.questions[0].description == "Choose the label that is your preference."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["Response 1", "Response 2"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown == False
    assert dataset.fields[1].name == "response1"
    assert dataset.fields[1].title == "Response 1"
    assert dataset.fields[1].use_markdown == False
    assert dataset.fields[2].name == "response2"
    assert dataset.fields[2].title == "Response 2"
    assert dataset.fields[2].use_markdown == False
    assert (
        dataset.guidelines
        == "This is a direct preference optimization dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
    )

    # Test case 2: With context and markdown
    dataset = FeedbackDataset.for_direct_preference_optimization(context=True, use_markdown=True)
    assert len(dataset) == 0
    assert dataset.questions[0].name == "preference"
    assert dataset.questions[0].description == "Choose the label that is your preference."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["Response 1", "Response 2"]
    assert dataset.fields[0].name == "context"
    assert dataset.fields[0].use_markdown == True
    assert dataset.fields[1].name == "prompt"
    assert dataset.fields[1].use_markdown == True
    assert dataset.fields[2].name == "response1"
    assert dataset.fields[2].title == "Response 1"
    assert dataset.fields[2].use_markdown == True
    assert dataset.fields[3].name == "response2"
    assert dataset.fields[3].title == "Response 2"
    assert dataset.fields[3].use_markdown == True
    assert (
        dataset.guidelines
        == "This is a direct preference optimization dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
    )
