# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from uuid import uuid4

import pytest

import argilla as rg


@pytest.fixture
def dataset():
    settings = rg.Settings(
        fields=[rg.TextField(name="prompt")],
        questions=[rg.LabelQuestion(name="label", labels=["negative", "positive"])],
        metadata=[rg.FloatMetadataProperty(name="score")],
        vectors=[rg.VectorField(name="vector", dimensions=3)],
    )
    workspace = rg.Workspace(name="workspace", id=uuid4())
    return rg.Dataset(
        name="test_dataset",
        settings=settings,
        workspace=workspace,
    )


def test_ingest_record_from_dict(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "What is the capital of France?",
            "label": "positive",
        },
    )

    assert record.fields["prompt"] == "What is the capital of France?"
    assert record.suggestions.label.value == "positive"


def test_ingest_record_from_dict_with_mapping(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "my_prompt": "What is the capital of France?",
            "label": "positive",
        },
        mapping={
            "my_prompt": "prompt",
        },
    )

    assert record.fields["prompt"] == "What is the capital of France?"
    assert record.suggestions.label.value == "positive"


def test_ingest_record_from_dict_with_suggestions(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions.label.value == "negative"


def test_ingest_record_from_dict_with_suggestions_scores(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "score": 0.9,
            "model": "model_name",
        },
        mapping={
            "score": "label.suggestion.score",
            "model": "label.suggestion.agent",
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions.label.value == "negative"
    assert record.suggestions.label.score == 0.9
    assert record.suggestions.label.agent == "model_name"


def test_ingest_record_from_dict_with_suggestions_scores_and_agent(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "score": 0.9,
            "model": "model_name",
        },
        mapping={
            "score": "label.suggestion.score",
            "model": "label.suggestion.agent",
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions.label.value == "negative"
    assert record.suggestions.label.score == 0.9
    assert record.suggestions.label.agent == "model_name"


def test_ingest_record_from_dict_with_responses(dataset):
    user_id = uuid4()
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
        },
        mapping={
            "label": "label.response",
        },
        user_id=user_id,
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.responses.label[0].value == "negative"
    assert record.responses.label[0].user_id == user_id


def test_ingest_record_from_dict_with_id_as_id(dataset):
    record_id = uuid4()
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "id": record_id,
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.id == record_id


def test_ingest_record_from_dict_with_id_and_mapping(dataset):
    record_id = uuid4()
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "test_id": record_id,
        },
        mapping={
            "test_id": "id",
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.id == record_id


def test_ingest_record_from_dict_with_metadata(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "score": 0.9,
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions.label.value == "negative"
    assert record.metadata["score"] == 0.9


def test_ingest_record_from_dict_with_metadata_and_mapping(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "test_score": 0.9,
        },
        mapping={
            "test_score": "score",
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions.label.value == "negative"
    assert record.metadata["score"] == 0.9


def test_ingest_record_from_dict_with_vectors(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "vector": [1, 2, 3],
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions.label.value == "negative"
    assert record.vectors["vector"] == [1, 2, 3]


def test_ingest_record_from_dict_with_vectors_and_mapping(dataset):
    record = dataset.records._infer_record_from_mapping(
        data={
            "prompt": "Hello World, how are you?",
            "label": "negative",
            "test_vector": [1, 2, 3],
        },
        mapping={
            "test_vector": "vector",
        },
    )

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions.label.value == "negative"
    assert record.vectors["vector"] == [1, 2, 3]
