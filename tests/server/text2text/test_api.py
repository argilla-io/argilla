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

from argilla.server.apis.v0.models.commons.model import BulkResponse
from argilla.server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextRecordInputs,
    Text2TextSearchResults,
)


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


def test_api_with_new_predictions_data_model(mocked_client):
    dataset = "test_api_with_new_predictions_data_model"
    delete_dataset(dataset, mocked_client)

    records = [
        Text2TextRecordInputs.parse_obj(
            {
                "text": "This is a text data",
                "predictions": {
                    "test": {
                        "sentences": [{"text": "This is a test data", "score": 0.6}]
                    },
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

    response = mocked_client.post(
        f"/api/datasets/{dataset}/Text2Text:bulk",
        json=Text2TextBulkRequest(
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 2

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


def delete_dataset(dataset, mocked_client):
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
