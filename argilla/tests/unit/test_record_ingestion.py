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
from argilla._exceptions import RecordsIngestionError


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
    record_api_models = dataset.records._ingest_records(
        records=[
            {
                "prompt": "What is the capital of France?",
                "label": "positive",
            }
        ],
    )

    record = record_api_models[0]
    assert record.fields["prompt"] == "What is the capital of France?"
    assert record.suggestions[0].value == "positive"


def test_ingest_record_from_empty_dict_raises(dataset):
    with pytest.raises(RecordsIngestionError):
        dataset.records._ingest_records(
            records=[
                {"id": "record_id"},
            ],
        )
    with pytest.raises(RecordsIngestionError):
        dataset.records._ingest_records(
            records=[
                {},
            ],
        )


def test_ingest_record_from_dict_with_mapped_suggestions(dataset):
    mock_mapping = {
        "my_prompt": "prompt",
        "my_label": "label.suggestion.value",
        "score": "label.suggestion.score",
        "model": "label.suggestion.agent",
    }
    record_api_models = dataset.records._ingest_records(
        records=[
            {
                "my_prompt": "What is the capital of France?",
                "my_label": "positive",
                "score": 0.9,
                "model": "model_name",
            }
        ],
        mapping=mock_mapping,
    )
    record = record_api_models[0]
    assert record.fields["prompt"] == "What is the capital of France?"
    assert record.suggestions[0].value == "positive"
    assert record.suggestions[0].question_name == "label"
    assert record.suggestions[0].score == 0.9
    assert record.suggestions[0].agent == "model_name"


def test_ingest_record_from_dict_with_mapped_responses(dataset):
    user_id = uuid4()
    mocked_mapping = {
        "label": "label.response",
    }
    record_api_models = dataset.records._ingest_records(
        records=[
            {
                "prompt": "Hello World, how are you?",
                "label": "negative",
            }
        ],
        mapping=mocked_mapping,
        user_id=user_id,
    )
    record = record_api_models[0]

    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.responses[0].values["label"]["value"] == "negative"
    assert record.responses[0].user_id == user_id


def test_ingest_record_from_dict_with_id_as_id(dataset):
    record_id = uuid4()
    record_api_models = dataset.records._ingest_records(
        records=[
            {
                "prompt": "Hello World, how are you?",
                "label": "negative",
                "id": record_id,
            }
        ],
    )
    record = record_api_models[0]
    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.external_id == record_id


def test_ingest_record_from_dict_with_mapped_id(dataset):
    record_id = uuid4()
    mock_mapping = {
        "test_id": "id",
    }
    record_api_models = dataset.records._ingest_records(
        records=[
            {
                "prompt": "Hello World, how are you?",
                "label": "negative",
                "test_id": record_id,
            }
        ],
        mapping=mock_mapping,
    )
    record_model = record_api_models[0]
    assert record_model.fields["prompt"] == "Hello World, how are you?"
    assert record_model.external_id == record_id


def test_ingest_record_from_dict_with_mapped_metadata_vectors(dataset):
    mock_mapping = {
        "test_score": "score",
        "test_vector": "vector",
    }
    record_api_models = dataset.records._ingest_records(
        records=[
            {
                "prompt": "Hello World, how are you?",
                "label": "negative",
                "test_score": 0.9,
                "test_vector": [1, 2, 3],
            }
        ],
        mapping=mock_mapping,
    )

    record = record_api_models[0]
    assert record.fields["prompt"] == "Hello World, how are you?"
    assert record.suggestions[0].value == "negative"
    assert record.vectors[0].vector_values == [1, 2, 3]
    assert record.vectors[0].name == "vector"
    assert record.metadata[0].value == 0.9
    assert record.metadata[0].name == "score"


def test_ingest_record_from_dict_with_mapping_multiple():
    settings = rg.Settings(
        fields=[rg.TextField(name="prompt_field")],
        questions=[
            rg.LabelQuestion(name="label", labels=["negative", "positive"]),
            rg.TextQuestion(name="prompt_question"),
        ],
    )
    workspace = rg.Workspace(name="workspace", id=uuid4())
    dataset = rg.Dataset(
        name="test_dataset",
        settings=settings,
        workspace=workspace,
    )
    mapping = {
        "my_prompt": ("prompt_field", "prompt_question"),
    }
    record_api_models = dataset.records._ingest_records(
        records=[
            {
                "my_prompt": "What is the capital of France?",
                "label": "positive",
            }
        ],
        mapping=mapping,
    )
    record = record_api_models[0]
    suggestions = [s.value for s in record.suggestions]
    assert record.fields["prompt_field"] == "What is the capital of France?"
    assert "positive" in suggestions
    assert "What is the capital of France?" in suggestions
