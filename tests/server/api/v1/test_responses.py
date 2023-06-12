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
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import DatasetStatus, Response, ResponseStatus, UserRole
from argilla.server.search_engine import SearchEngine
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    RecordFactory,
    ResponseFactory,
    TextQuestionFactory,
    UserFactory,
    WorkspaceFactory,
)


def test_update_response(client: TestClient, db: Session, mock_search_engine: SearchEngine, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)
    record = RecordFactory.create(dataset=dataset)

    response = ResponseFactory.create(
        record=record,
        values={"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
        status=ResponseStatus.submitted,
    )
    response_json = {
        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
        "status": "submitted",
    }

    resp = client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 200
    assert db.get(Response, response.id).values == {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}}

    resp_body = resp.json()
    assert resp_body == {
        "id": str(response.id),
        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
        "status": "submitted",
        "record_id": str(response.record_id),
        "user_id": str(response.user_id),
        "inserted_at": response.inserted_at.isoformat(),
        "updated_at": datetime.fromisoformat(resp_body["updated_at"]).isoformat(),
    }

    mock_search_engine.update_record_response.assert_called_once_with(response)


def test_update_response_without_authentication(client: TestClient, db: Session):
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        status="submitted",
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    resp = client.put(f"/api/v1/responses/{response.id}", json=response_json)

    assert resp.status_code == 401
    assert db.get(Response, response.id).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


def test_update_response_from_submitted_to_discarded(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)
    record = RecordFactory.create(dataset=dataset)

    response = ResponseFactory.create(
        record=record,
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        status="submitted",
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "discarded",
    }

    resp = client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 200

    response = db.get(Response, response.id)
    assert response.values == {
        "input_ok": {"value": "yes"},
        "output_ok": {"value": "yes"},
    }
    assert response.status == ResponseStatus.discarded

    resp_body = resp.json()
    assert resp_body == {
        "id": str(response.id),
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "discarded",
        "record_id": str(response.record_id),
        "user_id": str(response.user_id),
        "inserted_at": response.inserted_at.isoformat(),
        "updated_at": datetime.fromisoformat(resp_body["updated_at"]).isoformat(),
    }


def test_update_response_from_submitted_to_discarded_without_values(client: TestClient, db: Session, owner_auth_header):
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        status="submitted",
    )
    response_json = {
        "status": "discarded",
    }

    resp = client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 200

    response = db.get(Response, response.id)
    assert response.values == None
    assert response.status == ResponseStatus.discarded

    resp_body = resp.json()
    assert resp_body == {
        "id": str(response.id),
        "values": None,
        "status": "discarded",
        "record_id": str(response.record_id),
        "user_id": str(response.user_id),
        "inserted_at": response.inserted_at.isoformat(),
        "updated_at": datetime.fromisoformat(resp_body["updated_at"]).isoformat(),
    }


def test_update_response_from_discarded_to_submitted(client: TestClient, db: Session, owner_auth_header):
    response = ResponseFactory.create(status="discarded")
    response_json = {
        "status": "submitted",
    }

    resp = client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 422


def test_update_response_from_discarded_to_submitted_without_values(client: TestClient, db: Session, owner_auth_header):
    response = ResponseFactory.create(status="discarded")
    response_json = {
        "status": "submitted",
    }

    resp = client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 422

    response = db.get(Response, response.id)
    assert response.values == None
    assert response.status == ResponseStatus.discarded


def test_update_response_with_wrong_values(client: TestClient, db: Session, owner_auth_header):
    response = ResponseFactory.create(status="discarded")
    response_json = {"status": "submitted", "values": {"wrong_question": {"value": "wrong value"}}}

    resp = client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 422
    assert resp.json() == {"detail": "Error: found responses for non configured questions: ['wrong_question']"}

    response = db.get(Response, response.id)
    assert response.values is None
    assert response.status == ResponseStatus.discarded


def test_update_response_as_annotator(client: TestClient, db: Session):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)
    record = RecordFactory.create(dataset=dataset)
    annotator = AnnotatorFactory.create()

    response = ResponseFactory.create(
        record=record,
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        status="submitted",
        user=annotator,
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    resp = client.put(
        f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
    )

    assert resp.status_code == 200
    assert db.get(Response, response.id).values == {
        "input_ok": {"value": "yes"},
        "output_ok": {"value": "yes"},
    }

    resp_body = resp.json()
    assert resp_body == {
        "id": str(response.id),
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
        "record_id": str(response.record_id),
        "user_id": str(response.user_id),
        "inserted_at": response.inserted_at.isoformat(),
        "updated_at": datetime.fromisoformat(resp_body["updated_at"]).isoformat(),
    }


def test_update_response_as_annotator_for_different_user_response(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        status="submitted",
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    resp = client.put(
        f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
    )

    assert resp.status_code == 403
    assert db.get(Response, response.id).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


def test_update_response_with_nonexistent_response_id(client: TestClient, db: Session, owner_auth_header):
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        status="submitted",
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    resp = client.put(f"/api/v1/responses/{uuid4()}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 404
    assert db.get(Response, response.id).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


def test_delete_response(client: TestClient, mock_search_engine: SearchEngine, db: Session, owner_auth_header):
    response = ResponseFactory.create()

    resp = client.delete(f"/api/v1/responses/{response.id}", headers=owner_auth_header)

    assert resp.status_code == 200
    assert db.query(Response).count() == 0

    mock_search_engine.delete_record_response.assert_called_once_with(response)


def test_delete_response_without_authentication(client: TestClient, db: Session):
    response = ResponseFactory.create()

    resp = client.delete(f"/api/v1/responses/{response.id}")

    assert resp.status_code == 401
    assert db.query(Response).count() == 1


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
def test_delete_response_as_restricted_user(client: TestClient, db: Session, role: UserRole):
    user = UserFactory.create(role=role)
    response = ResponseFactory.create(user=user)

    resp = client.delete(f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: user.api_key})

    assert resp.status_code == 200
    assert db.query(Response).count() == 0


def test_delete_response_as_admin_for_different_user_response(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()
    admin = AdminFactory.create(workspaces=[workspace])
    response = ResponseFactory.create(record=RecordFactory.create(dataset=DatasetFactory.create(workspace=workspace)))

    resp = client.delete(f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert resp.status_code == 200
    assert db.query(Response).count() == 0


def test_delete_response_as_annotator_for_different_user_response(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    response = ResponseFactory.create()

    resp = client.delete(f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert resp.status_code == 403
    assert db.query(Response).count() == 1


def test_delete_response_with_nonexistent_response_id(client: TestClient, db: Session, owner_auth_header):
    ResponseFactory.create()

    resp = client.delete(f"/api/v1/responses/{uuid4()}", headers=owner_auth_header)

    assert resp.status_code == 404
    assert db.query(Response).count() == 1
