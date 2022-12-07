#  coding=utf-8
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
from typing import Callable

import pytest

from argilla.server.apis.v0.models.commons.model import BulkResponse, SortableField
from argilla.server.apis.v0.models.token_classification import (
    TokenClassificationBulkRequest,
    TokenClassificationQuery,
    TokenClassificationRecord,
    TokenClassificationSearchRequest,
    TokenClassificationSearchResults,
)
from tests.client.conftest import SUPPORTED_VECTOR_SEARCH


def test_load_as_different_task(mocked_client):
    dataset = "test_load_as_different_task"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    expected_text = "This is a text with !"
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": expected_text.split(" "),
                "raw_text": expected_text,
            }
        ]
    ]
    mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::WrongTaskError",
            "params": {
                "message": "Provided task TextClassification cannot be "
                "applied to dataset"
            },
        }
    }


def test_search_special_characters(mocked_client):
    dataset = "test_search_special_characters"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    expected_text = "This is a text with !"
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": expected_text.split(" "),
                "raw_text": expected_text,
            }
        ]
    ]
    mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json=TokenClassificationSearchRequest(
            query=TokenClassificationQuery(query_text="\!")
        ).dict(),
    )
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert results.total == 0

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json=TokenClassificationSearchRequest(
            query=TokenClassificationQuery(query_text="text.exact:\!")
        ).dict(),
    )
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1


def test_some_sort(mocked_client):
    dataset = "test_some_sort"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    expected_text = "This is a text with !"
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": expected_text.split(" "),
                "raw_text": expected_text,
            }
        ]
    ]
    mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json=TokenClassificationSearchRequest(
            sort=[SortableField(id="babba")],
        ).dict(),
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "Wrong sort id babba. Valid values are: "
                "['id', 'metadata', 'score', 'predicted', "
                "'predicted_as', 'predicted_by', "
                "'annotated_as', 'annotated_by', 'status', "
                "'last_updated', 'event_timestamp']"
            },
        }
    }


@pytest.mark.parametrize(
    ("include_metrics", "metrics_validator"),
    [
        (True, lambda r: len(r.metrics) > 0),
        (False, lambda r: len(r.metrics) == 0),
        (None, lambda r: len(r.metrics) == 0),
    ],
)
def test_create_records_for_token_classification(
    mocked_client, include_metrics: bool, metrics_validator: Callable
):
    dataset = "test_create_records_for_token_classification"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    entity_label = "TEST"
    expected_records = 2
    record = {
        "tokens": "This is a text".split(" "),
        "raw_text": "This is a text",
        "metadata": {"field_one": "value one", "field_two": "value 2"},
        "prediction": {
            "agent": "test",
            "entities": [{"start": 0, "end": 4, "label": entity_label}],
        },
        "annotation": {
            "agent": "test",
            "entities": [{"start": 0, "end": 4, "label": entity_label}],
        },
    }
    records = [TokenClassificationRecord.parse_obj(record)] * expected_records

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == expected_records

    search_url = f"/api/datasets/{dataset}/TokenClassification:search"
    if include_metrics is not None:
        search_url += f"?include_metrics={include_metrics}"

    response = mocked_client.post(search_url)
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())

    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {"TEST": 1},
        "annotated_by": {"test": 1},
        "mentions": {"TEST": {"This": 1}},
        "metadata": {"field_one": {"value one": 1}, "field_two": {"value 2": 1}},
        "predicted": {"ok": 1},
        "predicted_as": {"TEST": 1},
        "predicted_by": {"test": 1},
        "predicted_mentions": {"TEST": {"This": 1}},
        "status": {"Default": 1},
        "words": {},
    }

    assert "This" in results.aggregations.predicted_mentions[entity_label]
    assert "This" in results.aggregations.mentions[entity_label]
    for record in results.records:
        assert metrics_validator(record)


@pytest.mark.skipif(
    condition=not SUPPORTED_VECTOR_SEARCH,
    reason="Vector search not supported",
)
@pytest.mark.parametrize(
    ("include_metrics", "metrics_validator"),
    [
        (True, lambda r: len(r.metrics) > 0),
        (False, lambda r: len(r.metrics) == 0),
        (None, lambda r: len(r.metrics) == 0),
    ],
)
def test_create_records_for_token_classification_vector_search(
    mocked_client,
    include_metrics: bool,
    metrics_validator: Callable,
):
    dataset = "test_create_records_for_token_classification_vector_search"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    entity_label = "TEST"
    expected_records = 3
    record_dicts = [
        {
            "id": 0,
            "tokens": "This is a text".split(" "),
            "raw_text": "This is a text",
            "metadata": {"field_one": "value one", "field_two": "value 2"},
            "prediction": {
                "agent": "test",
                "entities": [{"start": 0, "end": 4, "label": entity_label}],
            },
            "annotation": {
                "agent": "test",
                "entities": [{"start": 0, "end": 4, "label": entity_label}],
            },
            "vectors": {"my_bert": {"value": [1, 2, 3, 4, 5, 6]}},
        },
        {
            "id": 1,
            "tokens": "This is a text".split(" "),
            "raw_text": "This is a text",
            "metadata": {"field_one": "value one", "field_two": "value 2"},
            "prediction": {
                "agent": "test",
                "entities": [{"start": 0, "end": 4, "label": entity_label}],
            },
            "annotation": {
                "agent": "test",
                "entities": [{"start": 0, "end": 4, "label": entity_label}],
            },
            "vectors": {"my_bert": {"value": [5, 6, 7, 8, 9, 10]}},
        },
        {
            "id": 2,
            "tokens": "This is a text".split(" "),
            "raw_text": "This is a text",
            "metadata": {"field_one": "value one", "field_two": "value 2"},
            "prediction": {
                "agent": "test",
                "entities": [{"start": 0, "end": 4, "label": entity_label}],
            },
            "annotation": {
                "agent": "test",
                "entities": [{"start": 0, "end": 4, "label": entity_label}],
            },
            "vectors": {"my_bert": {"value": [7, 8, 9, 10, 11, 12]}},
        },
    ]

    records = [TokenClassificationRecord.parse_obj(record) for record in record_dicts]

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == expected_records

    search_url = f"/api/datasets/{dataset}/TokenClassification:search"
    if include_metrics is not None:
        search_url += f"?include_metrics={include_metrics}"

    response = mocked_client.post(
        search_url,
        json={
            "query": {
                "vector_name": "my_bert",
                "vector_value": [5, 6, 7, 8, 9, 10],
            }
        },
    )
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())

    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {"TEST": 3},
        "annotated_by": {"test": 3},
        "mentions": {"TEST": {"This": 3}},
        "metadata": {"field_one": {"value one": 3}, "field_two": {"value 2": 3}},
        "predicted": {"ok": 3},
        "predicted_as": {"TEST": 3},
        "predicted_by": {"test": 3},
        "predicted_mentions": {"TEST": {"This": 3}},
        "status": {"Default": 3},
        "words": {},
    }

    assert "This" in results.aggregations.predicted_mentions[entity_label]
    assert "This" in results.aggregations.mentions[entity_label]
    expected_record_ids = [1, 2, 0]
    for index, record in enumerate(results.records):
        assert metrics_validator(record)
        assert expected_record_ids[index] == record.id
        assert hasattr(record, "vectors")


def test_multiple_mentions_in_same_record(mocked_client):
    dataset = "test_multiple_mentions_in_same_record"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    entity_a, entity_b = ("TESTA", "TESTB")

    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "prediction": {
                    "agent": "test",
                    "entities": [
                        {"start": 0, "end": 4, "label": entity_a},
                        {"start": 5, "end": 7, "label": entity_b},
                    ],
                },
            },
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "prediction": {
                    "agent": "test",
                    "entities": [{"start": 0, "end": 4, "label": entity_a}],
                },
            },
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "annotation": {
                    "agent": "test",
                    "entities": [{"start": 0, "end": 4, "label": entity_a}],
                },
            },
        ]
    ]
    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 3

    response = mocked_client.post(f"/api/datasets/{dataset}/TokenClassification:search")
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert "This" in results.aggregations.predicted_mentions[entity_a]
    assert results.aggregations.predicted_mentions[entity_a]["This"] == 2
    assert "is" in results.aggregations.predicted_mentions[entity_b]
    assert results.aggregations.predicted_mentions[entity_b]["is"] == 1


def test_show_not_aggregable_metadata_fields(mocked_client):
    dataset = "test_show_not_aggregable_metadata_fields"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            records=[
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 1.3, "field_two": 2},
                    },
                ),
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 2.3, "field_two": 300},
                    },
                ),
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 11.333, "field_two": -10},
                    },
                ),
            ],
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json={},
    )
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert len(results.aggregations.metadata) == 2
    assert "field_one" in results.aggregations.metadata
    assert "argilla:stats" in results.aggregations.metadata["field_one"]
