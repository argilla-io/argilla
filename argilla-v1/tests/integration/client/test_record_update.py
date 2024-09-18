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

import pytest
from argilla_server.models import User
from argilla_v1.client.sdk.commons.errors import NotFoundApiError
from argilla_v1.client.singleton import active_api, init


def test_partial_update_with_not_found(argilla_user: User, gutenberg_spacy_ner: str):
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)
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


def record_data_by_id(*, dataset: str, record_id: str):
    data = active_api().datasets.scan(
        name=dataset,
        query=f"id: {record_id}",
        projection={"metadata"},
    )

    for record in data:
        return record
