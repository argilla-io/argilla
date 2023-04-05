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
from uuid import UUID, uuid4

from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import Annotation, AnnotationType, Dataset
from argilla.server.schemas.v1.datasets import RATING_MAX_ITEMS, RATING_MIN_ITEMS
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import (
    AnnotationFactory,
    AnnotatorFactory,
    DatasetFactory,
    RatingAnnotationFactory,
    TextAnnotationFactory,
    WorkspaceFactory,
)


def test_list_datasets(client: TestClient, admin_auth_header: dict):
    dataset_a = DatasetFactory.create(name="dataset-a")
    dataset_b = DatasetFactory.create(name="dataset-b", guidelines="guidelines")
    dataset_c = DatasetFactory.create(name="dataset-c")

    response = client.get("/api/v1/datasets", headers=admin_auth_header)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(dataset_a.id),
            "name": "dataset-a",
            "guidelines": None,
            "workspace_id": str(dataset_a.workspace_id),
            "inserted_at": dataset_a.inserted_at.isoformat(),
            "updated_at": dataset_a.updated_at.isoformat(),
        },
        {
            "id": str(dataset_b.id),
            "name": "dataset-b",
            "guidelines": "guidelines",
            "workspace_id": str(dataset_b.workspace_id),
            "inserted_at": dataset_b.inserted_at.isoformat(),
            "updated_at": dataset_b.updated_at.isoformat(),
        },
        {
            "id": str(dataset_c.id),
            "name": "dataset-c",
            "guidelines": None,
            "workspace_id": str(dataset_c.workspace_id),
            "inserted_at": dataset_c.inserted_at.isoformat(),
            "updated_at": dataset_c.updated_at.isoformat(),
        },
    ]


def test_list_datasets_without_authentication(client: TestClient):
    response = client.get("/api/v1/datasets")

    assert response.status_code == 401


def test_list_datasets_as_annotator(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[workspace])

    DatasetFactory.create(name="dataset-a", workspace=workspace)
    DatasetFactory.create(name="dataset-b", workspace=workspace)
    DatasetFactory.create(name="dataset-c")

    response = client.get("/api/v1/datasets", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200
    assert [dataset["name"] for dataset in response.json()] == ["dataset-a", "dataset-b"]


def test_get_dataset(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create(name="dataset")

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers=admin_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "id": str(dataset.id),
        "name": "dataset",
        "guidelines": None,
        "workspace_id": str(dataset.workspace_id),
        "inserted_at": dataset.inserted_at.isoformat(),
        "updated_at": dataset.updated_at.isoformat(),
    }


def test_get_dataset_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}")

    assert response.status_code == 401


def test_get_dataset_as_annotator(client: TestClient, db: Session):
    dataset = DatasetFactory.create(name="dataset")
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200
    assert response.json()["name"] == "dataset"


def test_get_dataset_as_annotator_from_different_workspace(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_get_dataset_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404


def test_get_dataset_annotations(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    text_annotation = TextAnnotationFactory.create(
        name="text-annotation", title="Text Annotation", required=True, dataset=dataset
    )
    rating_annotation = RatingAnnotationFactory.create(
        name="rating-annotation", title="Rating Annotation", dataset=dataset
    )
    TextAnnotationFactory.create()
    RatingAnnotationFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/annotations", headers=admin_auth_header)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(text_annotation.id),
            "name": "text-annotation",
            "title": "Text Annotation",
            "type": AnnotationType.text.value,
            "required": True,
            "settings": {},
            "inserted_at": text_annotation.inserted_at.isoformat(),
            "updated_at": text_annotation.updated_at.isoformat(),
        },
        {
            "id": str(rating_annotation.id),
            "name": "rating-annotation",
            "title": "Rating Annotation",
            "type": AnnotationType.rating.value,
            "required": False,
            "settings": {},
            "inserted_at": rating_annotation.inserted_at.isoformat(),
            "updated_at": rating_annotation.updated_at.isoformat(),
        },
    ]


def test_get_dataset_annotations_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/annotations")

    assert response.status_code == 401


def test_get_dataset_annotations_as_annotator(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])
    TextAnnotationFactory.create(name="text-annotation", dataset=dataset)
    RatingAnnotationFactory.create(name="rating-annotation", dataset=dataset)
    TextAnnotationFactory.create()
    RatingAnnotationFactory.create()

    response = client.get(
        f"/api/v1/datasets/{dataset.id}/annotations", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 200
    assert [annotation["name"] for annotation in response.json()] == ["text-annotation", "rating-annotation"]


def test_get_dataset_annotations_as_annotator_from_different_workspace(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(
        f"/api/v1/datasets/{dataset.id}/annotations", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403


def test_get_dataset_annotations_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}/annotations", headers=admin_auth_header)

    assert response.status_code == 404


def test_create_dataset(client: TestClient, db: Session, admin_auth_header: dict):
    workspace = WorkspaceFactory.create()
    dataset_json = {"name": "name", "guidelines": "guidelines", "workspace_id": str(workspace.id)}

    response = client.post("/api/v1/datasets", headers=admin_auth_header, json=dataset_json)

    assert response.status_code == 201
    assert db.query(Dataset).count() == 1

    response_body = response.json()
    assert db.get(Dataset, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "name": "name",
        "guidelines": "guidelines",
        "workspace_id": str(workspace.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_dataset_without_authentication(client: TestClient, db: Session):
    dataset_json = {"name": "name", "workspace_id": str(WorkspaceFactory.create().id)}

    response = client.post("/api/v1/datasets", json=dataset_json)

    assert response.status_code == 401
    assert db.query(Dataset).count() == 0


def test_create_dataset_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset_json = {"name": "name", "workspace_id": str(WorkspaceFactory.create().id)}

    response = client.post("/api/v1/datasets", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=dataset_json)

    assert response.status_code == 403
    assert db.query(Dataset).count() == 0


def test_create_dataset_with_existent_name(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(name="name")
    dataset_json = {"name": "name", "workspace_id": str(dataset.workspace_id)}

    response = client.post("/api/v1/datasets", headers=admin_auth_header, json=dataset_json)

    assert response.status_code == 409
    assert db.query(Dataset).count() == 1


def test_create_dataset_annotation(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "name",
        "title": "title",
        "type": AnnotationType.text.value,
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/annotations", headers=admin_auth_header, json=annotation_json
    )

    assert response.status_code == 201
    assert db.query(Annotation).count() == 1

    response_body = response.json()
    assert db.get(Annotation, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "name": "name",
        "title": "title",
        "type": AnnotationType.text.value,
        "required": False,
        "settings": {},
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_dataset_annotation_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "name",
        "title": "title",
        "type": AnnotationType.text.value,
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/annotations", json=annotation_json)

    assert response.status_code == 401
    assert db.query(Annotation).count() == 0


def test_create_dataset_annotation_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "name",
        "title": "title",
        "type": AnnotationType.text.value,
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/annotations",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
        json=annotation_json,
    )

    response.status_code == 403
    assert db.query(Annotation).count() == 0


def test_create_dataset_annotation_with_existent_name(client: TestClient, db: Session, admin_auth_header: dict):
    annotation = AnnotationFactory.create(name="name")
    annotation_json = {"name": "name", "title": "title", "type": AnnotationType.text.value}

    response = client.post(
        f"/api/v1/datasets/{annotation.dataset.id}/annotations", headers=admin_auth_header, json=annotation_json
    )

    assert response.status_code == 409
    assert db.query(Annotation).count() == 1


def test_create_dataset_annotation_with_nonexistent_dataset_id(
    client: TestClient, db: Session, admin_auth_header: dict
):
    DatasetFactory.create()
    annotation_json = {
        "name": "text",
        "title": "Text",
        "type": AnnotationType.text.value,
        "settings": {"discarded": "values"},
    }

    response = client.post(f"/api/v1/datasets/{uuid4()}/annotations", headers=admin_auth_header, json=annotation_json)

    assert response.status_code == 404
    assert db.query(Annotation).count() == 0


def test_create_dataset_text_annotation(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "text",
        "title": "Text",
        "type": AnnotationType.text.value,
        "settings": {"discarded": "value"},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/annotations", headers=admin_auth_header, json=annotation_json
    )

    assert response.status_code == 201
    assert db.query(Annotation).count() == 1

    response_body = response.json()
    assert db.get(Annotation, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "name": "text",
        "title": "Text",
        "type": AnnotationType.text.value,
        "required": False,
        "settings": {},
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_dataset_rating_annotation(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "rating",
        "title": "Rating",
        "type": AnnotationType.rating.value,
        "settings": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/annotations", headers=admin_auth_header, json=annotation_json
    )

    assert response.status_code == 201
    assert db.query(Annotation).count() == 1

    response_body = response.json()
    assert db.get(Annotation, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "name": "rating",
        "title": "Rating",
        "type": AnnotationType.rating.value,
        "required": False,
        "settings": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_dataset_rating_annotation_with_less_values_than_allowed(
    client: TestClient, db: Session, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "rating",
        "title": "Rating",
        "type": AnnotationType.rating.value,
        "settings": {"values": list(range(0, RATING_MIN_ITEMS - 1))},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/annotations", headers=admin_auth_header, json=annotation_json
    )

    assert response.status_code == 422
    assert db.query(Annotation).count() == 0


def test_create_dataset_rating_annotation_with_more_values_than_allowed(
    client: TestClient, db: Session, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "rating",
        "title": "Rating",
        "type": AnnotationType.rating.value,
        "settings": {"values": list(range(0, RATING_MAX_ITEMS + 1))},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/annotations", headers=admin_auth_header, json=annotation_json
    )

    assert response.status_code == 422
    assert db.query(Annotation).count() == 0


def test_create_dataset_rating_annotation_with_invalid_settings(
    client: TestClient, db: Session, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    annotation_json = {
        "name": "rating",
        "title": "Rating",
        "type": AnnotationType.rating.value,
        "settings": {"invalid": "value"},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/annotations", headers=admin_auth_header, json=annotation_json
    )

    assert response.status_code == 422
    assert db.query(Annotation).count() == 0


def test_delete_dataset(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers=admin_auth_header)

    assert response.status_code == 200
    assert db.query(Dataset).count() == 0


def test_delete_dataset_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{dataset.id}")

    assert response.status_code == 401
    assert db.query(Dataset).count() == 1


def test_delete_dataset_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset = DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.query(Dataset).count() == 1


def test_delete_dataset_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.query(Dataset).count() == 1
