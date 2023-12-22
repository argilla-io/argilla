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

import argilla.client.singleton
import datasets
import pytest
from argilla import User, Workspace
from argilla.client.feedback.config import DatasetConfig
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.questions import TextQuestion
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.schemas.remote.records import RemoteSuggestionSchema
from argilla.client.feedback.schemas.vector_settings import VectorSettings
from argilla.client.feedback.training.schemas.base import TrainingTask
from argilla.client.models import Framework

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.server.models import User as ServerUser
    from sqlalchemy.ext.asyncio import AsyncSession

    from tests.integration.helpers import SecuredClient


def test_create_dataset_with_suggestions(argilla_user: "ServerUser") -> None:
    argilla.client.singleton.init(api_key=argilla_user.api_key)

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
    argilla.client.singleton.init(api_key=argilla_user.api_key)

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


def test_add_records_with_vectors() -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="text", required=True)],
        questions=[TextQuestion(name="question-1", required=True)],
        vectors_settings=[
            VectorSettings(name="vector-1", dimensions=3),
            VectorSettings(name="vector-2", dimensions=4),
        ],
    )

    dataset.add_records(
        [
            FeedbackRecord(
                fields={"text": "Text"},
                vectors={
                    "vector-1": [1.0, 2.0, 3.0],
                },
            ),
            FeedbackRecord(
                fields={"text": "Text"},
                vectors={
                    "vector-1": [1.0, 2.0, 3.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                },
            ),
        ]
    )

    assert len(dataset.records) == 2
    assert dataset.records[0].vectors == {"vector-1": [1.0, 2.0, 3.0]}
    assert dataset.records[1].vectors == {"vector-1": [1.0, 2.0, 3.0], "vector-2": [1.0, 2.0, 3.0, 4.0]}


@pytest.mark.parametrize(
    "record, exception_cls, exception_msg",
    [
        (FeedbackRecord(fields={}, metadata={}), ValueError, "required-field\n  field required"),
        (
            FeedbackRecord(fields={"optional-field": "text"}, metadata={}),
            ValueError,
            "required-field\n  field required",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"terms-metadata": "d"}),
            ValueError,
            "terms-metadata\n  Provided 'terms-metadata=d' is not valid, only values in \['a', 'b', 'c'\] are allowed.",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"int-metadata": 11}),
            ValueError,
            "int-metadata\n  Provided 'int-metadata=11' is not valid, only values between 0 and 10 are allowed.",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"float-metadata": 11.0}),
            ValueError,
            "float-metadata\n  Provided 'float-metadata=11.0' is not valid, only values between 0.0 and 10.0 are allowed.",
        ),
    ],
)
def test_add_records_validation_error(
    record: FeedbackRecord, exception_cls: Exception, exception_msg: str, argilla_user: "ServerUser"
) -> None:
    argilla.client.singleton.init(api_key=argilla_user.api_key)

    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )

    remote_dataset = dataset.push_to_argilla(name="my-dataset")

    with pytest.raises(exception_cls, match=exception_msg):
        remote_dataset.add_records(record)

    assert len(dataset.records) == 0
    remote_dataset.delete()


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
    argilla.client.singleton.active_api()
    argilla.client.singleton.init(api_key="argilla.apikey")

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
    argilla.client.singleton.active_api()
    argilla.client.singleton.init(api_key=argilla_user.api_key)

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
    argilla.client.singleton.active_api()
    argilla.client.singleton.init(api_key=argilla_user.api_key)

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
    argilla.client.singleton.active_api()
    argilla.client.singleton.init(api_key=argilla_user.api_key)

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


def test_push_to_huggingface_and_from_huggingface(
    mocked_client: "SecuredClient",
    monkeypatch: pytest.MonkeyPatch,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    argilla.client.singleton.active_api()
    argilla.client.singleton.init(api_key="argilla.apikey")

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
    owner: "ServerUser",
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

    argilla.client.singleton.init(api_key=owner.api_key)
    ws = Workspace.create(name="test-workspace")

    remote = dataset.push_to_argilla(name="test-dataset", workspace=ws)

    label = remote.question_by_name(question)
    task = TrainingTask.for_text_classification(text=dataset.fields[0], label=label)

    data = remote.prepare_for_training(framework=framework, task=task)
    assert data is not None


def test_push_to_argilla_with_vector_settings(argilla_user: User):
    argilla.client.singleton.init(api_key=argilla_user.api_key)

    dataset = FeedbackDataset(
        fields=[TextField(name="required-field")],
        questions=[TextQuestion(name="question")],
        vectors_settings=[VectorSettings(name="vector-settings", dimensions=100)],
    )

    remote = dataset.push_to_argilla(name="test-dataset-vector01")
    assert len(remote.vectors_settings) == 1
    assert remote.vectors_settings[0].name == "vector-settings"
    assert remote.vectors_settings[0].dimensions == 100


def test_add_vector_settings():
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field")],
        questions=[TextQuestion(name="question")],
    )

    expected_settings = VectorSettings(name="vector-settings", dimensions=100)
    new_settings = dataset.add_vector_settings(expected_settings)
    assert expected_settings == new_settings
    assert len(dataset.vectors_settings) == 1
    assert dataset.vector_settings_by_name("vector-settings") == expected_settings


def test_add_duplicated_vector_settings():
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field")],
        questions=[TextQuestion(name="question")],
    )

    expected_settings = VectorSettings(name="vector-settings", dimensions=100)
    dataset.add_vector_settings(expected_settings)

    with pytest.raises(ValueError, match="Vector settings with name 'vector-settings' already exists"):
        dataset.add_vector_settings(expected_settings)


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_warning_remote_dataset_methods(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )

    with pytest.warns(
        UserWarning, match="`pull` method is not supported for local datasets and won't take any effect."
    ):
        dataset.pull()

    with pytest.warns(
        UserWarning, match="`filter_by` method is not supported for local datasets and won't take any effect."
    ):
        dataset.filter_by()

    with pytest.warns(
        UserWarning, match="`delete` method is not supported for local datasets and won't take any effect."
    ):
        dataset.delete()
