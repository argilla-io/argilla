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
from typing import TYPE_CHECKING, Awaitable, Callable
from uuid import UUID, uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import Record, Response, User
from argilla.server.search_engine import SearchEngine
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextQuestionFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from argilla.server.models import Dataset
    from sqlalchemy.ext.asyncio import AsyncSession


async def create_text_questions(dataset: "Dataset") -> None:
    await TextQuestionFactory.create(name="input_ok", dataset=dataset, required=True)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)


async def create_rating_questions(dataset: "Dataset") -> None:
    await RatingQuestionFactory.create(name="rating_question_1", dataset=dataset, required=True)
    await RatingQuestionFactory.create(name="rating_question_2", dataset=dataset)


async def create_label_selection_questions(dataset: "Dataset") -> None:
    await LabelSelectionQuestionFactory.create(name="label_selection_question_1", dataset=dataset, required=True)
    await LabelSelectionQuestionFactory.create(name="label_selection_question_2", dataset=dataset)


async def create_multi_label_selection_questions(dataset: "Dataset") -> None:
    await MultiLabelSelectionQuestionFactory.create(
        name="multi_label_selection_question_1", dataset=dataset, required=True
    )
    await MultiLabelSelectionQuestionFactory.create(name="multi_label_selection_question_2", dataset=dataset)


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
    ],
)
@pytest.mark.asyncio
async def test_create_record_response_with_required_questions(
    client: TestClient,
    db: "AsyncSession",
    mock_search_engine: SearchEngine,
    admin: User,
    admin_auth_header: dict,
    create_questions_func: Callable[["Dataset"], Awaitable[None]],
    response_status: str,
    responses: dict,
):
    dataset = await DatasetFactory.create()
    await create_questions_func(dataset)
    record = await RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": response_status}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    response_body = response.json()
    assert response.status_code == 201
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
    assert await db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": responses["values"],
        "status": response_status,
        "user_id": str(admin.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }

    response = (await db.execute(select(Response).where(Response.record_id == record.id))).scalar_one()
    mock_search_engine.update_record_response.assert_called_once_with(response)


@pytest.mark.asyncio
async def test_create_submitted_record_response_with_missing_required_questions(
    client: TestClient, admin_auth_header: dict
):
    dataset = await DatasetFactory.create()
    await create_text_questions(dataset)

    record = await RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {"output_ok": {"value": "yes"}},
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)
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
    ],
)
@pytest.mark.asyncio
async def test_create_record_response_with_missing_required_questions(
    client: TestClient,
    db: "AsyncSession",
    mock_search_engine: SearchEngine,
    admin: User,
    admin_auth_header: dict,
    create_questions_func: Callable[["Dataset"], Awaitable[None]],
    response_status: str,
    responses: dict,
):
    dataset = await DatasetFactory.create()
    await create_questions_func(dataset)
    record = await RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": response_status}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    response_body = response.json()
    assert response.status_code == 201
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
    assert await db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": responses["values"],
        "status": response_status,
        "user_id": str(admin.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }

    response = (await db.execute(select(Response).where(Response.record_id == record.id))).scalar_one()
    mock_search_engine.update_record_response.assert_called_once_with(response)


@pytest.mark.asyncio
async def test_create_record_response_with_extra_question_responses(client: TestClient, admin_auth_header: dict):
    dataset = await DatasetFactory.create()
    await create_text_questions(dataset)
    record = await RecordFactory.create(dataset=dataset)

    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "unknown_question": {"value": "Test"},
        },
        "status": "submitted",
    }
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
            "Expected list of values, found <class 'str'>",
        ),
        (
            create_multi_label_selection_questions,
            {
                "values": {
                    "multi_label_selection_question_1": {"value": ["option4", "option5"]},
                },
            },
            "['option4', 'option5'] are not valid options.\nValid options are: ['option1', 'option2', 'option3']",
        ),
        (
            create_multi_label_selection_questions,
            {"values": {"multi_label_selection_question_1": {"value": []}}},
            "Expected list of values, found empty list",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_record_response_with_wrong_response_value(
    client: TestClient,
    admin_auth_header: dict,
    create_questions_func: Callable[["Dataset"], None],
    responses: dict,
    expected_error_msg: str,
):
    dataset = await DatasetFactory.create()
    await create_questions_func(dataset)
    record = await RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": "submitted"}
    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert response.json() == {"detail": expected_error_msg}


@pytest.mark.asyncio
async def test_create_record_response_without_authentication(client: TestClient, db: "AsyncSession"):
    record = await RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", json=response_json)

    assert response.status_code == 401
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.parametrize("status", ["submitted", "discarded", "draft"])
@pytest.mark.asyncio
async def test_create_record_response(
    client: TestClient, db: "AsyncSession", admin: User, admin_auth_header: dict, status: str
):
    dataset = await DatasetFactory.create()
    await TextQuestionFactory.create(name="input_ok", dataset=dataset)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = await RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": status,
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 201
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

    response_body = response.json()
    assert await db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": status,
        "user_id": str(admin.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


@pytest.mark.parametrize(
    "status, expected_status_code, expected_response_count",
    [("submitted", 422, 0), ("discarded", 201, 1), ("draft", 422, 0)],
)
@pytest.mark.asyncio
async def test_create_record_response_without_values(
    client: TestClient,
    db: "AsyncSession",
    admin: User,
    admin_auth_header: dict,
    status: str,
    expected_status_code: int,
    expected_response_count: int,
):
    record = await RecordFactory.create()
    response_json = {"status": status}

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == expected_status_code
    assert (await db.execute(select(func.count(Response.id)))).scalar() == expected_response_count

    if expected_status_code == 201:
        response_body = response.json()
        assert await db.get(Response, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "values": None,
            "status": "discarded",
            "user_id": str(admin.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }


@pytest.mark.parametrize("status", ["submitted", "discarded", "draft"])
@pytest.mark.asyncio
async def test_create_record_submitted_response_with_wrong_values(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict, status: str
):
    record = await RecordFactory.create()
    response_json = {"status": status, "values": {"wrong_question": {"value": "wrong value"}}}

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Error: found responses for non configured questions: ['wrong_question']"}
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_record_response_as_annotator(client: TestClient, db: "AsyncSession"):
    dataset = await DatasetFactory.create()
    await TextQuestionFactory.create(name="input_ok", dataset=dataset)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = await RecordFactory.create(dataset=dataset)
    annotator = await AnnotatorFactory.create(workspaces=[record.dataset.workspace])
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
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

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


@pytest.mark.asyncio
async def test_create_record_response_as_annotator_from_different_workspace(client: TestClient, db: "AsyncSession"):
    record = await RecordFactory.create()
    annotator = await AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])
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
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_record_response_already_created(
    client: TestClient, db: "AsyncSession", admin: User, admin_auth_header: dict
):
    record = await RecordFactory.create()
    await ResponseFactory.create(record=record, user=admin)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 409
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_record_response_with_invalid_values(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict
):
    record = await RecordFactory.create()
    response_json = {
        "values": "invalid",
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_record_response_with_invalid_status(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict
):
    record = await RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "invalid",
    }

    response = client.post(f"/api/v1/records/{record.id}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_record_response_with_nonexistent_record_id(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict
):
    await RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = client.post(f"/api/v1/records/{uuid4()}/responses", headers=admin_auth_header, json=response_json)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
