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
from uuid import UUID

from argilla.server.models import DatasetStatus, Record, Response, User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import DatasetFactory, RecordFactory


def test_create_records(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {"fields": {"input": "input-a", "output": "output-a"}, "external_id": "a"},
            {"fields": {"input": "input-b", "output": "output-b"}, "external_id": "b"},
            {
                "fields": {"input": "input-c", "output": "output-c"},
                "external_id": "c",
                "response": {"question": {"value": True}},
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 204
    assert db.query(Record).count() == 3


def test_create_response(client: TestClient, db: Session, admin: User, admin_auth_header: dict):
    dataset = DatasetFactory.build(status=DatasetStatus.ready)
    record = RecordFactory.create(dataset=dataset)

    response_json = {
        "question_01": {"value": True},
        "question-02": {"value": 10},
    }

    response = client.put(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)
    assert response.status_code == 200

    assert db.query(Response).count() == 1

    stored_response = db.query(Response).filter_by(record_id=record.id, user_id=admin.id).first()

    assert stored_response
    assert response.json() == stored_response.values
