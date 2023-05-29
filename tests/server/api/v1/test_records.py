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
from typing import TYPE_CHECKING, Callable
from uuid import UUID, uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import Response, User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    LabelSelectionQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextQuestionFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from argilla.server.models import Dataset


def create_text_questions(dataset: "Dataset") -> None:
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)


def create_rating_questions(dataset: "Dataset") -> None:
    RatingQuestionFactory.create(name="rating_question", dataset=dataset, required=False)


def create_label_selection_questions(dataset: "Dataset") -> None:
    LabelSelectionQuestionFactory.create(name="label_selection_question", dataset=dataset, required=False)


@pytest.mark.parametrize(
    "create_questions_func, responses",
    [
        (
            create_text_questions,
            {
                "values": {
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
            },
        ),
        (
            create_rating_questions,
            {
                "values": {
                    "rating_question": {"value": 5},
                },
            },
        ),
        (
            create_label_selection_questions,
            {
                "values": {
                    "label_selection_question": {"value": "option1"},
                },
            },
        ),
    ],
)
def test_create_record_response(
    client: TestClient,
    db: Session,
    admin: User,
    admin_auth_header: dict,
    create_questions_func: Callable[["Dataset"], None],
    responses: dict,
):
    dataset = DatasetFactory.create()
    create_questions_func(dataset)
    record = RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": "submitted"}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    response_body = response.json()
    assert response.status_code == 201
    assert db.query(Response).count() == 1
    assert db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": responses["values"],
        "status": "submitted",
        "user_id": str(admin.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


@pytest.mark.parametrize(
    "create_questions_func, responses",
    [
        (
            create_text_questions,
            {
                "values": {
                    "input_ok": {"value": "yes"},
                    "unknown_question": {"value": "Test"},
                },
            },
        ),
        (
            create_rating_questions,
            {
                "values": {
                    "rating_question": {"value": 5},
                    "unknown_question": {"value": "Test"},
                },
            },
        ),
        (
            create_label_selection_questions,
            {
                "values": {
                    "label_selection_question": {"value": "option1"},
                    "unknown_question": {"value": "Test"},
                },
            },
        ),
    ],
)
def test_create_record_response_with_extra_question_responses(
    client: TestClient,
    db: Session,
    admin_auth_header: dict,
    create_questions_func: Callable[["Dataset"], None],
    responses: dict,
):
    dataset = DatasetFactory.create()
    create_questions_func(dataset)
    record = RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": "submitted"}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Error: found responses for non configured questions: ['unknown_question']"}


@pytest.mark.parametrize(
    "create_questions_func, responses, expected_error_msg",
    [
        (
            create_text_questions,
            {
                "values": {
                    "input_ok": {"value": True},
                    "output_ok": {"value": False},
                },
            },
            "Expected text value, found <class 'bool'>",
        ),
        (
            create_rating_questions,
            {
                "values": {
                    "rating_question": {"value": "wrong-rating-value"},
                },
            },
            "'wrong-rating-value' is not a valid option.\nValid options are: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
        ),
        (
            create_label_selection_questions,
            {
                "values": {
                    "label_selection_question": {"value": False},
                },
            },
            "False is not a valid option.\nValid options are: ['option1', 'option2', 'option3']",
        ),
    ],
)
def test_create_record_response_with_wrong_response_value(
    client: TestClient,
    db: Session,
    admin_auth_header: dict,
    create_questions_func: Callable[["Dataset"], None],
    responses: dict,
    expected_error_msg: str,
):
    dataset = DatasetFactory.create()
    create_questions_func(dataset)
    record = RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": "submitted"}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert response.json() == {"detail": expected_error_msg}


def test_create_submitted_record_response_with_missing_required_questions(
    client: TestClient, db: Session, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    TextQuestionFactory.create(name="input_ok", dataset=dataset, required=True)
    TextQuestionFactory.create(name="output_ok", dataset=dataset, required=True)

    record = RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {"input_ok": {"value": "yes"}},
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Missing required question: 'output_ok'"}


def test_create_record_response_without_authentication(client: TestClient, db: Session):
    record = RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", json=response_json)

    assert response.status_code == 401
    assert db.query(Response).count() == 0


def test_create_record_submitted_response(client: TestClient, db: Session, admin: User, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 201
    assert db.query(Response).count() == 1

    response_body = response.json()
    assert db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
        "user_id": str(admin.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_record_submitted_response_without_values(client: TestClient, db: Session, admin_auth_header: dict):
    record = RecordFactory.create()
    response_json = {"status": "submitted"}

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert db.query(Response).count() == 0


def test_create_record_submitted_response_with_wrong_values(client: TestClient, db: Session, admin_auth_header: dict):
    record = RecordFactory.create()
    response_json = {"status": "submitted", "values": {"wrong_question": {"value": "wrong value"}}}

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Error: found responses for non configured questions: ['wrong_question']"}
    assert db.query(Response).count() == 0


def test_create_record_discarded_response(client: TestClient, db: Session, admin: User, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        "status": "discarded",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 201
    assert db.query(Response).count() == 1

    response_body = response.json()
    assert db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": {
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        "status": "discarded",
        "user_id": str(admin.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_record_discarded_response_without_values(
    client: TestClient, db: Session, admin: User, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = RecordFactory.create(dataset=dataset)
    response_json = {"status": "discarded"}

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 201
    assert db.query(Response).count() == 1

    response_body = response.json()
    assert db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": None,
        "status": "discarded",
        "user_id": str(admin.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_record_response_as_annotator(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = RecordFactory.create(dataset=dataset)
    annotator = AnnotatorFactory.create(workspaces=[record.dataset.workspace])
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(
        f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
    )

    assert response.status_code == 201
    assert db.query(Response).count() == 1

    response_body = response.json()
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
        "user_id": str(annotator.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_record_response_as_annotator_from_different_workspace(client: TestClient, db: Session):
    record = RecordFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(
        f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
    )

    assert response.status_code == 403
    assert db.query(Response).count() == 0


def test_create_record_response_already_created(client: TestClient, db: Session, admin: User, admin_auth_header: dict):
    record = RecordFactory.create()
    ResponseFactory.create(record=record, user=admin)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 409
    assert db.query(Response).count() == 1


def test_create_record_response_with_invalid_values(client: TestClient, db: Session, admin_auth_header: dict):
    record = RecordFactory.create()
    response_json = {
        "values": "invalid",
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert db.query(Response).count() == 0


def test_create_record_response_with_invalid_status(client: TestClient, db: Session, admin_auth_header: dict):
    record = RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "invalid",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert db.query(Response).count() == 0


def test_create_record_response_with_nonexistent_record_id(client: TestClient, db: Session, admin_auth_header: dict):
    RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{uuid4()}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 404
    assert db.query(Response).count() == 0
