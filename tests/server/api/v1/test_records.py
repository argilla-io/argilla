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

from datetime import datetime
from uuid import UUID

from argilla.server.models import Response, User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import RecordFactory, ResponseFactory


# TODO: Rest of tests for create record reponse
def test_create_record_response(client: TestClient, db: Session, admin_auth_header: dict):
    record = RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": "yes",
            "output_ok": "yes",
        },
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 201
    assert db.query(Response).count() == 1

    response_body = response.json()
    assert db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": {
            "input_ok": "yes",
            "output_ok": "yes",
        },
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_record_response_already_created(client: TestClient, db: Session, admin: User, admin_auth_header: dict):
    record = RecordFactory.create()
    ResponseFactory.create(record=record, user=admin)
    response_json = {
        "values": {
            "input_ok": "yes",
            "output_ok": "yes",
        },
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 409
    assert db.query(Response).count() == 1
