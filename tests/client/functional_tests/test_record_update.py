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
from time import sleep

import pytest
from argilla.client.api import active_api
from argilla.client.sdk.commons.errors import NotFoundApiError


def test_partial_update_with_not_found(mocked_client, gutenberg_spacy_ner):
    with pytest.raises(NotFoundApiError):
        active_api().datasets.update_record(
            name=gutenberg_spacy_ner,
            record_id="NOT_FOUND",
            metadata={"meta": "data"},
        )


def test_partial_record_update(mocked_client, gutenberg_spacy_ner):
    expected_id = "00c27206-da48-4fc3-aab7-4b730628f8ac"

    record = record_data_by_id(
        dataset=gutenberg_spacy_ner,
        record_id=expected_id,
    )
    assert not record.get("metadata")

    metadata_update = {"new_key": "new_label"}
    record = active_api().datasets.update_record(
        name=gutenberg_spacy_ner,
        record_id=expected_id,
        metadata=metadata_update,
    )
    assert record["id"] == expected_id

    record = record_data_by_id(
        dataset=gutenberg_spacy_ner,
        record_id=expected_id,
    )
    assert record["metadata"] == metadata_update

    new_metadata_update = {
        "other": "field",
    }
    active_api().datasets.update_record(
        name=gutenberg_spacy_ner,
        record_id=expected_id,
        metadata=new_metadata_update,
    )
    record = record_data_by_id(
        dataset=gutenberg_spacy_ner,
        record_id=expected_id,
    )
    assert record["metadata"] == {
        **metadata_update,
        **new_metadata_update,
    }


def test_batch_update(mocked_client, gutenberg_spacy_ner):
    records = active_api().datasets.scan(name=gutenberg_spacy_ner, projection={"text", "prediction"}, limit=10)
    records = list(records)

    records_update = [
        {"id": record["id"], "data": {"annotation": {"agent": "me", "entities": record["prediction"]["entities"][:1]}}}
        for record in records
    ]

    dataset = active_api().datasets.find_by_name(gutenberg_spacy_ner)
    response = mocked_client.post(
        f"/api/datasets/{dataset.id}/records/:batch-update",
        json={"records": records_update},
    )

    assert response.status_code == 200
    assert response.json() == {"not_found_ids": [], "updated": 10}

    ds = active_api().load(name=gutenberg_spacy_ner, ids=[record["id"] for record in records])

    for record in ds:
        assert record.annotation_agent
        assert record.annotation


def test_batch_update_with_not_found(mocked_client, gutenberg_spacy_ner):
    records_update = [
        {"id": -100, "data": {"annotation": {"agent": "me"}}},
        {"id": -200, "data": {"annotation": {"agent": "you"}}},
    ]

    dataset = active_api().datasets.find_by_name(gutenberg_spacy_ner)
    response = mocked_client.post(
        f"/api/datasets/{dataset.id}/records/:batch-update",
        json={"records": records_update},
    )

    assert response.status_code == 200
    assert response.json() == {"not_found_ids": ["-100", "-200"], "updated": 0}


def record_data_by_id(*, dataset: str, record_id: str):
    data = active_api().datasets.scan(
        name=dataset,
        query=f"id: {record_id}",
        projection={"metadata"},
    )

    for record in data:
        return record
