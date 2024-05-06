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

import uuid

import pytest
from argilla_server.commons.models import TaskType
from argilla_server.daos.backend import GenericElasticEngineBackend
from argilla_server.daos.backend.search.model import BaseRecordsQuery
from argilla_server.errors import InvalidTextSearchError


@pytest.fixture(scope="session")
def engine():
    return GenericElasticEngineBackend.get_instance()


@pytest.fixture
def dataset_id(engine: GenericElasticEngineBackend):
    dataset_id = str(uuid.uuid4())

    yield dataset_id

    engine.delete(dataset_id)


def test_creating_index_with_non_searchable_metadata(engine: GenericElasticEngineBackend, dataset_id: str):
    engine.create_dataset(
        id=dataset_id,
        task=TaskType.text_classification,
        metadata_values={
            "a": "value",
            "other": "value",
            "_this": "is non searchable",
            "_other": "other disabled field",
        },
        force_recreate=True,
    )

    # Check the schema definition
    schema = engine.get_schema(dataset_id)
    assert schema["mappings"]["properties"]["metadata"]["properties"]["_this"] == {"type": "object", "enabled": False}
    assert schema["mappings"]["properties"]["metadata"]["properties"]["_other"] == {"type": "object", "enabled": False}


def test_non_searchable_docs_are_not_present_in_metrics(engine: GenericElasticEngineBackend, dataset_id: str):
    engine.create_dataset(
        id=dataset_id,
        task=TaskType.text_classification,
        metadata_values={"a": "value", "other": "value", "_this": "is non searchable"},
        force_recreate=True,
    )

    docs = [{"text": "This is my text", "metadata": {"_this": "value"}}] * 100
    assert engine.add_dataset_records(dataset_id, documents=docs) == 0

    metric_results = engine.compute_metric(dataset_id, metric_id="metadata")
    assert metric_results == {}


def test_non_searchable_fields_are_present_in_documents(engine: GenericElasticEngineBackend, dataset_id: str):
    engine.create_dataset(
        id=dataset_id,
        task=TaskType.text_classification,
        metadata_values={
            "a": "value",
            "other": "value",
            "_this": "is non searchable",
            "_other": "other disabled field",
        },
        force_recreate=True,
    )
    documents = [
        {"id": f"{i:03d}", "text": "This is my text", "metadata": {"_this": "value", "_other": {"with": "key"}}}
        for i in range(0, 100)
    ]

    assert engine.add_dataset_records(dataset_id, documents=documents) == 0

    total, results = engine.search_records(dataset_id, size=5)
    assert total == 100
    assert results == documents[:5]


def test_non_searchable_fields_cannot_be_used_for_search(engine: GenericElasticEngineBackend, dataset_id: str):
    engine.create_dataset(
        id=dataset_id,
        task=TaskType.text_classification,
        metadata_values={"a": "value", "_protected": "is non searchable", "non_protected": "normal field"},
        force_recreate=True,
    )
    documents = [
        {"id": f"{i:03d}", "text": "This is my text", "metadata": {"_protected": "value", "non_protected": "value"}}
        for i in range(0, 100)
    ]

    assert engine.add_dataset_records(dataset_id, documents=documents) == 0

    total, _ = engine.search_records(id=dataset_id, query=BaseRecordsQuery(query_text="metadata.non_protected:value"))
    assert total == 100

    total, _ = engine.search_records(id=dataset_id, query=BaseRecordsQuery(query_text="metadata._protected:value"))
    assert total == 0
