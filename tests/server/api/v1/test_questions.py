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
from argilla.server.models import DatasetStatus, Question
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import AnnotatorFactory, DatasetFactory, TextQuestionFactory


def test_delete_question(client: TestClient, db: Session, owner_auth_header):
    question = TextQuestionFactory.create(name="name", title="title", description="description")

    response = client.delete(f"/api/v1/questions/{question.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert db.query(Question).count() == 0

    response_body = response.json()
    assert response_body == {
        "id": str(question.id),
        "name": "name",
        "title": "title",
        "description": "description",
        "required": False,
        "settings": {"type": "text", "use_markdown": False},
        "dataset_id": str(question.dataset_id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_delete_question_without_authentication(client: TestClient, db: Session):
    question = TextQuestionFactory.create()

    response = client.delete(f"/api/v1/questions/{question.id}")

    assert response.status_code == 401
    assert db.query(Question).count() == 1


def test_delete_question_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    question = TextQuestionFactory.create()

    response = client.delete(f"/api/v1/questions/{question.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.query(Question).count() == 1


def test_delete_question_belonging_to_published_dataset(client: TestClient, db: Session, owner_auth_header):
    question = TextQuestionFactory.create(dataset=DatasetFactory.build(status=DatasetStatus.ready))

    response = client.delete(f"/api/v1/questions/{question.id}", headers=owner_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Questions cannot be deleted for a published dataset"}
    assert db.query(Question).count() == 1


def test_delete_question_with_nonexistent_question_id(client: TestClient, db: Session, owner_auth_header):
    TextQuestionFactory.create()

    response = client.delete(f"/api/v1/questions/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert db.query(Question).count() == 1
