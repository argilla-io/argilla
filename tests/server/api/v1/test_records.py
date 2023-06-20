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
from argilla.server.models import Record, Response, User, UserRole
from argilla.server.search_engine import SearchEngine
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import (
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextQuestionFactory,
    UserFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from argilla.server.models import Dataset


def create_text_questions(dataset: "Dataset") -> None:
    TextQuestionFactory.create(name="input_ok", dataset=dataset, required=True)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)


def create_rating_questions(dataset: "Dataset") -> None:
    RatingQuestionFactory.create(name="rating_question_1", dataset=dataset, required=True)
    RatingQuestionFactory.create(name="rating_question_2", dataset=dataset)


def create_label_selection_questions(dataset: "Dataset") -> None:
    LabelSelectionQuestionFactory.create(name="label_selection_question_1", dataset=dataset, required=True)
    LabelSelectionQuestionFactory.create(name="label_selection_question_2", dataset=dataset)


def create_multi_label_selection_questions(dataset: "Dataset") -> None:
    MultiLabelSelectionQuestionFactory.create(name="multi_label_selection_question_1", dataset=dataset, required=True)
    MultiLabelSelectionQuestionFactory.create(name="multi_label_selection_question_2", dataset=dataset)


def create_ranking_question(dataset: "Dataset") -> None:
    RankingQuestionFactory.create(name="ranking_question_1", dataset=dataset, required=True)
    RankingQuestionFactory.create(name="ranking_question_2", dataset=dataset)


@pytest.mark.parametrize("response_status", ["submitted", "discarded", "draft"])
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
                    "rating_question_1": {"value": 5},
                },
            },
        ),
        (
            create_label_selection_questions,
            {
                "values": {
                    "label_selection_question_1": {"value": "option1"},
                },
            },
        ),
        (
            create_multi_label_selection_questions,
            {
                "values": {
                    "multi_label_selection_question_1": {"value": ["option1"]},
                },
            },
        ),
        (
            create_multi_label_selection_questions,
            {
                "values": {
                    "multi_label_selection_question_1": {"value": ["option1", "option2"]},
                },
            },
        ),
        (
            create_text_questions,
            {
                "values": {
                    "input_ok": {"value": "yes"},
                },
            },
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_1": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                            {"value": "completion-c", "rank": 2},
                            {"value": "completion-a", "rank": 3},
                        ]
                    },
                }
            },
        ),
    ],
)
def test_create_record_response_with_required_questions(
    client: TestClient,
    db: Session,
    mock_search_engine: SearchEngine,
    owner,
    owner_auth_header,
    create_questions_func: Callable[["Dataset"], None],
    response_status: str,
    responses: dict,
):
    dataset = DatasetFactory.create()
    create_questions_func(dataset)
    record = RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": response_status}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    response_body = response.json()
    assert response.status_code == 201
    assert db.query(Response).count() == 1
    assert db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": responses["values"],
        "status": response_status,
        "user_id": str(owner.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }

    mock_search_engine.update_record_response.assert_called_once_with(
        db.query(Response).where(Record.id == record.id).first()
    )


def test_create_submitted_record_response_with_missing_required_questions(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    create_text_questions(dataset)

    record = RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {"output_ok": {"value": "yes"}},
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Missing required question: 'input_ok'"}


@pytest.mark.parametrize("response_status", ["discarded", "draft"])
@pytest.mark.parametrize(
    "create_questions_func, responses",
    [
        (
            create_text_questions,
            {
                "values": {
                    "output_ok": {"value": "yes"},
                },
            },
        ),
        (
            create_rating_questions,
            {
                "values": {
                    "rating_question_2": {"value": 5},
                },
            },
        ),
        (
            create_label_selection_questions,
            {
                "values": {
                    "label_selection_question_2": {"value": "option1"},
                },
            },
        ),
        (
            create_multi_label_selection_questions,
            {
                "values": {
                    "multi_label_selection_question_2": {"value": ["option1"]},
                },
            },
        ),
        (
            create_multi_label_selection_questions,
            {
                "values": {
                    "multi_label_selection_question_2": {"value": ["option1", "option2"]},
                },
            },
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_2": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                            {"value": "completion-c", "rank": 2},
                            {"value": "completion-a", "rank": 3},
                        ]
                    },
                }
            },
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_2": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                            {"value": "completion-c", "rank": 1},
                            {"value": "completion-a", "rank": 3},
                        ]
                    },
                }
            },
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_2": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                            {"value": "completion-c", "rank": 3},
                            {"value": "completion-a", "rank": 3},
                        ]
                    },
                }
            },
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_2": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                            {"value": "completion-c", "rank": 1},
                            {"value": "completion-a", "rank": 1},
                        ]
                    },
                }
            },
        ),
    ],
)
def test_create_record_response_with_missing_required_questions(
    client: TestClient,
    db: Session,
    mock_search_engine: SearchEngine,
    owner,
    owner_auth_header,
    create_questions_func: Callable[["Dataset"], None],
    response_status: str,
    responses: dict,
):
    dataset = DatasetFactory.create()
    create_questions_func(dataset)
    record = RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": response_status}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    response_body = response.json()
    assert response.status_code == 201
    assert db.query(Response).count() == 1
    assert db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": responses["values"],
        "status": response_status,
        "user_id": str(owner.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }

    mock_search_engine.update_record_response.assert_called_once_with(
        db.query(Response).where(Record.id == record.id).first()
    )


def test_create_record_response_with_extra_question_responses(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    create_text_questions(dataset)
    record = RecordFactory.create(dataset=dataset)

    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "unknown_question": {"value": "Test"},
        },
        "status": "submitted",
    }
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

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
                    "rating_question_1": {"value": "wrong-rating-value"},
                },
            },
            "'wrong-rating-value' is not a valid option.\nValid options are: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
        ),
        (
            create_label_selection_questions,
            {
                "values": {
                    "label_selection_question_1": {"value": False},
                },
            },
            "False is not a valid option.\nValid options are: ['option1', 'option2', 'option3']",
        ),
        (
            create_multi_label_selection_questions,
            {
                "values": {
                    "multi_label_selection_question_1": {"value": "wrong-type"},
                },
            },
            "This MultiLabelSelection question expects a list of values, found <class 'str'>",
        ),
        (
            create_multi_label_selection_questions,
            {
                "values": {
                    "multi_label_selection_question_1": {"value": ["option4", "option5"]},
                },
            },
            "['option4', 'option5'] are not valid options for this MultiLabelSelection question.\nValid options are: ['option1', 'option2', 'option3']",
        ),
        (
            create_multi_label_selection_questions,
            {"values": {"multi_label_selection_question_1": {"value": []}}},
            "This MultiLabelSelection question expects a list of values, found empty list",
        ),
        (
            create_ranking_question,
            {"values": {"ranking_question_1": {"value": "wrong-type"}}},
            "This Ranking question expects a list of values, found <class 'str'>",
        ),
        (
            create_ranking_question,
            {"values": {"ranking_question_1": {"value": []}}},
            "This Ranking question expects a list containing 3 values, found a list of 0 values",
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_1": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                        ]
                    }
                }
            },
            "This Ranking question expects a list containing 3 values, found a list of 1 values",
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_1": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                            {"value": "completion-c", "rank": 2},
                            {"value": "completion-a", "rank": 3},
                            {"value": "completion-z", "rank": 4},
                        ],
                    }
                }
            },
            "This Ranking question expects a list containing 3 values, found a list of 4 values",
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_1": {
                        "value": [
                            {"value": "completion-b", "rank": 1},
                            {"value": "completion-c", "rank": 2},
                            {"value": "completion-a", "rank": 4},
                        ]
                    }
                }
            },
            "[4] are not valid ranks for this Ranking question.\nValid ranks are: [1, 2, 3]",
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_1": {
                        "value": [
                            {"value": "completion-b"},
                            {"value": "completion-c"},
                            {"value": "completion-a"},
                        ]
                    }
                }
            },
            "[None] are not valid ranks for this Ranking question.\nValid ranks are: [1, 2, 3]",
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_1": {
                        "value": [
                            {"value": "completion-z", "rank": 1},
                            {"value": "completion-c", "rank": 2},
                            {"value": "completion-a", "rank": 3},
                        ]
                    }
                }
            },
            "['completion-z'] are not valid options for this Ranking question.\nValid options are: ['completion-a', 'completion-b', 'completion-c']",
        ),
        (
            create_ranking_question,
            {
                "values": {
                    "ranking_question_1": {
                        "value": [
                            {"value": "completion-a", "rank": 1},
                            {"value": "completion-c", "rank": 2},
                            {"value": "completion-a", "rank": 3},
                        ]
                    }
                }
            },
            "This Ranking question expects a list of unique values, but duplicates were found",
        ),
    ],
)
def test_create_record_response_with_wrong_response_value(
    client: TestClient,
    db: Session,
    owner_auth_header,
    create_questions_func: Callable[["Dataset"], None],
    responses: dict,
    expected_error_msg: str,
):
    dataset = DatasetFactory.create()
    create_questions_func(dataset)
    record = RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": "submitted"}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    assert response.status_code == 422
    assert response.json() == {"detail": expected_error_msg}


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


@pytest.mark.parametrize("status", ["submitted", "discarded", "draft"])
def test_create_record_response(client: TestClient, db: Session, owner, owner_auth_header, status: str):
    dataset = DatasetFactory.create()
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": status,
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

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
        "status": status,
        "user_id": str(owner.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


@pytest.mark.parametrize(
    "status, expected_status_code, expected_response_count",
    [("submitted", 422, 0), ("discarded", 201, 1), ("draft", 422, 0)],
)
def test_create_record_response_without_values(
    client: TestClient,
    db: Session,
    owner,
    owner_auth_header,
    status: str,
    expected_status_code: int,
    expected_response_count: int,
):
    record = RecordFactory.create()
    response_json = {"status": status}

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    assert response.status_code == expected_status_code
    assert db.query(Response).count() == expected_response_count

    if expected_status_code == 201:
        response_body = response.json()
        assert db.get(Response, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "values": None,
            "status": "discarded",
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }


@pytest.mark.parametrize("status", ["submitted", "discarded", "draft"])
def test_create_record_submitted_response_with_wrong_values(
    client: TestClient, db: Session, owner_auth_header, status: str
):
    record = RecordFactory.create()
    response_json = {"status": status, "values": {"wrong_question": {"value": "wrong value"}}}

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Error: found responses for non configured questions: ['wrong_question']"}
    assert db.query(Response).count() == 0


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
def test_create_record_response_for_user_role(client: TestClient, db: Session, role: UserRole):
    dataset = DatasetFactory.create()
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = RecordFactory.create(dataset=dataset)
    user = UserFactory.create(workspaces=[record.dataset.workspace], role=role)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(
        f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: user.api_key}, json=response_json
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
        "user_id": str(user.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
def test_create_record_response_as_restricted_user_from_different_workspace(
    client: TestClient, db: Session, role: UserRole
):
    record = RecordFactory.create()
    user = UserFactory.create(workspaces=[WorkspaceFactory.build()], role=role)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(
        f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: user.api_key}, json=response_json
    )

    assert response.status_code == 403
    assert db.query(Response).count() == 0


def test_create_record_response_already_created(client: TestClient, db: Session, owner, owner_auth_header):
    record = RecordFactory.create()
    ResponseFactory.create(record=record, user=owner)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    assert response.status_code == 409
    assert db.query(Response).count() == 1


def test_create_record_response_with_invalid_values(client: TestClient, db: Session, owner_auth_header):
    record = RecordFactory.create()
    response_json = {
        "values": "invalid",
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    assert response.status_code == 422
    assert db.query(Response).count() == 0


def test_create_record_response_with_invalid_status(client: TestClient, db: Session, owner_auth_header):
    record = RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "invalid",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json)

    assert response.status_code == 422
    assert db.query(Response).count() == 0


def test_create_record_response_with_nonexistent_record_id(client: TestClient, db: Session, owner_auth_header):
    RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{uuid4()}/responses", headers=owner_auth_header, json=response_json)

    assert response.status_code == 404
    assert db.query(Response).count() == 0
