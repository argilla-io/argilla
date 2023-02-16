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
from typing import List, Optional

import pytest
from argilla.server.apis.v0.models.commons.model import BulkResponse
from argilla.server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextRecordInputs,
    Text2TextSearchResults,
)

from tests.client.conftest import SUPPORTED_VECTOR_SEARCH


def test_search_records(mocked_client):
    dataset = "test_search_records"
    delete_dataset(dataset, mocked_client)

    records = [
        Text2TextRecordInputs.parse_obj(data)
        for data in [
            {
                "id": 0,
                "text": "This is a text data",
                "metadata": {
                    "field_one": "value one",
                },
                "prediction": {
                    "agent": "test",
                    "sentences": [{"text": "This is a test data", "score": 0.6}],
                },
            },
            {
                "id": 1,
                "text": "Ånother data",
            },
        ]
    ]
    response = mocked_client.post(
        f"/api/datasets/{dataset}/Text2Text:bulk",
        json=Text2TextBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 2

    response = mocked_client.post(f"/api/datasets/{dataset}/Text2Text:search", json={})
    assert response.status_code == 200, response.json()
    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == 2
    assert results.records[0].predicted is None

    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {},
        "annotated_by": {},
        "annotated_text": {},
        "metadata": {"field_one": {"value one": 1}},
        "predicted": {},
        "predicted_as": {},
        "predicted_by": {"test": 1},
        "predicted_text": {},
        "status": {"Default": 2},
        "words": {
            "data": 2,
            "text": 1,
            "ånother": 1,
        },
    }


def search_data(
    *,
    client,
    base_url: str,
    expected_total: int,
    body: Optional[dict] = None,
    vector_name: Optional[str] = None,
):
    response = client.post(
        url=f"{base_url}:search",
        json=body or {},
    )
    assert response.status_code == 200, response.json()
    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == expected_total
    for record in results.records:
        print("\n Record info: \n")
        print(record.dict())
        if vector_name:
            assert record.vectors is not None
            assert vector_name in record.vectors


@pytest.mark.skipif(
    condition=not SUPPORTED_VECTOR_SEARCH,
    reason="Vector search not supported",
)
def test_search_with_vectors(mocked_client):
    dataset = "test_search_with_vectors"

    delete_dataset(dataset, mocked_client)

    records_for_text2text_with_vectors = [
        Text2TextRecordInputs.parse_obj(data)
        for data in [
            {
                "id": 0,
                "text": "This is a text data",
                "metadata": {
                    "field_one": "value one",
                },
                "prediction": {
                    "agent": "test",
                    "sentences": [{"text": "This is a test data", "score": 0.6}],
                },
                "vectors": {"my_bert": {"value": [1, 2, 3, 4]}},
            },
            {
                "id": 1,
                "text": "Ånother data",
                "vectors": {"my_bert": {"value": [4, 5, 6, 7]}},
            },
            {
                "id": 3,
                "text": "This is another text data",
                "prediction": {
                    "agent": "test",
                    "sentences": [{"text": "This is another test data", "score": 0.6}],
                },
            },
        ]
    ]

    base_url = prepare_data(
        client=mocked_client,
        dataset=dataset,
        records=records_for_text2text_with_vectors,
    )

    search_data(
        client=mocked_client,
        base_url=base_url,
        expected_total=2,
        vector_name="my_bert",
        body={
            "query": {
                "vector": {
                    "name": "my_bert",
                    "value": [1.2, 2.3, 4.1, 6.1],
                }
            }
        },
    )


def test_api_with_new_predictions_data_model(mocked_client):
    dataset = "test_api_with_new_predictions_data_model"
    delete_dataset(dataset, mocked_client)

    records = [
        Text2TextRecordInputs.parse_obj(
            {
                "text": "This is a text data",
                "predictions": {
                    "test": {"sentences": [{"text": "This is a test data", "score": 0.6}]},
                },
            }
        ),
        Text2TextRecordInputs.parse_obj(
            {
                "text": "Another data",
                "annotations": {
                    "annotator-1": {"sentences": [{"text": "THis is a test data"}]},
                    "annotator-2": {"sentences": [{"text": "This IS the test datay"}]},
                },
            }
        ),
    ]

    prepare_data(
        client=mocked_client,
        dataset=dataset,
        records=records,
    )

    response = mocked_client.post(
        f"/api/datasets/{dataset}/Text2Text:search",
        json={"query": {"query_text": "predictions.test.sentences.text.exact:data"}},
    )

    assert response.status_code == 200, response.json()
    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == 1, results

    response = mocked_client.post(
        f"/api/datasets/{dataset}/Text2Text:search",
        json={"query": {"query_text": "_exists_:annotations.annotator-1"}},
    )

    assert response.status_code == 200, response.json()
    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == 1, results


def prepare_data(*, client, dataset: str, records: List[Text2TextRecordInputs]):
    base_api_url = f"/api/datasets/{dataset}/Text2Text"
    response = client.post(
        f"{base_api_url}:bulk",
        json=Text2TextBulkRequest(
            records=records,
        ).dict(by_alias=True),
    )
    assert response.status_code == 200, response.json()

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == len(records)

    return base_api_url


def delete_dataset(dataset, mocked_client):
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
