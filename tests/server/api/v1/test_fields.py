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
from argilla.server.models import DatasetStatus, Field
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import AnnotatorFactory, DatasetFactory, TextFieldFactory


def test_delete_field(client: TestClient, db: Session, owner_auth_header):
    field = TextFieldFactory.create(name="name", title="title")

    response = client.delete(f"/api/v1/fields/{field.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert db.query(Field).count() == 0

    response_body = response.json()
    assert response_body == {
        "id": str(field.id),
        "name": "name",
        "title": "title",
        "required": False,
        "settings": {"type": "text", "use_markdown": False},
        "dataset_id": str(field.dataset.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_delete_field_without_authentication(client: TestClient, db: Session):
    field = TextFieldFactory.create()

    response = client.delete(f"/api/v1/fields/{field.id}")

    assert response.status_code == 401
    assert db.query(Field).count() == 1


def test_delete_field_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    field = TextFieldFactory.create()

    response = client.delete(f"/api/v1/fields/{field.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.query(Field).count() == 1


def test_delete_field_belonging_to_published_dataset(client: TestClient, db: Session, owner_auth_header):
    field = TextFieldFactory.create(dataset=DatasetFactory.build(status=DatasetStatus.ready))

    response = client.delete(f"/api/v1/fields/{field.id}", headers=owner_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Fields cannot be deleted for a published dataset"}
    assert db.query(Field).count() == 1


def test_delete_field_with_nonexistent_field_id(client: TestClient, db: Session, owner_auth_header):
    TextFieldFactory.create()

    response = client.delete(f"/api/v1/fields/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert db.query(Field).count() == 1
