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
from uuid import uuid4

from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import Response
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import AnnotatorFactory, ResponseFactory


def test_update_response(client: TestClient, db: Session, admin_auth_header: dict):
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        }
    }

    resp = client.put(f"/api/v1/responses/{response.id}", headers=admin_auth_header, json=response_json)

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
        "inserted_at": response.inserted_at.isoformat(),
        "updated_at": datetime.fromisoformat(resp_body["updated_at"]).isoformat(),
    }


def test_update_response_without_authentication(client: TestClient, db: Session):
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        }
    }

    resp = client.put(f"/api/v1/responses/{response.id}", json=response_json)

    assert resp.status_code == 401
    assert db.get(Response, response.id).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


def test_update_response_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        user=annotator,
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        }
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
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        }
    }

    resp = client.put(
        f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
    )

    assert resp.status_code == 403
    assert db.get(Response, response.id).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


def test_update_response_with_nonexistent_response_id(client: TestClient, db: Session, admin_auth_header: dict):
    response = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
    )
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        }
    }

    resp = client.put(f"/api/v1/responses/{uuid4()}", headers=admin_auth_header, json=response_json)

    assert resp.status_code == 404
    assert db.get(Response, response.id).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }
