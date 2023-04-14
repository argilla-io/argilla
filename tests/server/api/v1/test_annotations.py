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

from uuid import uuid4

from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import Annotation, DatasetStatus
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import AnnotatorFactory, DatasetFactory, TextAnnotationFactory


def test_delete_annotation(client: TestClient, db: Session, admin_auth_header: dict):
    annotation = TextAnnotationFactory.create()

    response = client.delete(f"/api/v1/annotations/{annotation.id}", headers=admin_auth_header)

    assert response.status_code == 200
    assert db.query(Annotation).count() == 0


def test_delete_annotation_without_authentication(client: TestClient, db: Session):
    annotation = TextAnnotationFactory.create()

    response = client.delete(f"/api/v1/annotations/{annotation.id}")

    assert response.status_code == 401
    assert db.query(Annotation).count() == 1


def test_delete_annotation_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    annotation = TextAnnotationFactory.create()

    response = client.delete(f"/api/v1/annotations/{annotation.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.query(Annotation).count() == 1


def test_delete_annotation_belonging_to_published_dataset(client: TestClient, db: Session, admin_auth_header: dict):
    annotation = TextAnnotationFactory.create(dataset=DatasetFactory.build(status=DatasetStatus.ready))

    response = client.delete(f"/api/v1/annotations/{annotation.id}", headers=admin_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Annotations cannot be deleted for a published dataset"}
    assert db.query(Annotation).count() == 1


def test_delete_annotation_with_nonexistent_annotation_id(client: TestClient, db: Session, admin_auth_header: dict):
    TextAnnotationFactory.create()

    response = client.delete(f"/api/v1/annotations/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.query(Annotation).count() == 1
