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
from argilla.server.models import Record, Response, Suggestion, User, UserRole
from argilla.server.search_engine import SearchEngine
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tests.factories import (
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    SuggestionFactory,
    TextQuestionFactory,
    UserFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from argilla.server.models import Dataset
    from httpx import AsyncClient
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


async def create_ranking_question(dataset: "Dataset") -> None:
    await RankingQuestionFactory.create(name="ranking_question_1", dataset=dataset, required=True)
    await RankingQuestionFactory.create(name="ranking_question_2", dataset=dataset)


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
@pytest.mark.asyncio
async def test_create_record_response_with_required_questions(
    async_client: "AsyncClient",
    db: "AsyncSession",
    mock_search_engine: SearchEngine,
    owner: User,
    owner_auth_header: dict,
    create_questions_func: Callable[["Dataset"], Awaitable[None]],
    response_status: str,
    responses: dict,
):
    dataset = await DatasetFactory.create()
    await create_questions_func(dataset)
    record = await RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": response_status}
    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    response_body = response.json()
    assert response.status_code == 201
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
    assert await db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": responses["values"],
        "status": response_status,
        "user_id": str(owner.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }

    response = (await db.execute(select(Response).where(Response.record_id == record.id))).scalar_one()
    mock_search_engine.update_record_response.assert_called_once_with(response)


@pytest.mark.asyncio
async def test_create_submitted_record_response_with_missing_required_questions(
    async_client: "AsyncClient", owner_auth_header: dict
):
    dataset = await DatasetFactory.create()
    await create_text_questions(dataset)

    record = await RecordFactory.create(dataset=dataset)
    response_json = {
        "values": {"output_ok": {"value": "yes"}},
        "status": "submitted",
    }

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )
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
@pytest.mark.asyncio
async def test_create_record_response_with_missing_required_questions(
    async_client: "AsyncClient",
    db: "AsyncSession",
    mock_search_engine: SearchEngine,
    owner: User,
    owner_auth_header: dict,
    create_questions_func: Callable[["Dataset"], Awaitable[None]],
    response_status: str,
    responses: dict,
):
    dataset = await DatasetFactory.create()
    await create_questions_func(dataset)
    record = await RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": response_status}
    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    response_body = response.json()
    assert response.status_code == 201
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
    assert await db.get(Response, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "values": responses["values"],
        "status": response_status,
        "user_id": str(owner.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }

    response = (await db.execute(select(Response).where(Response.record_id == record.id))).scalar_one()
    mock_search_engine.update_record_response.assert_called_once_with(response)


@pytest.mark.asyncio
async def test_create_record_response_with_extra_question_responses(
    async_client: "AsyncClient", owner_auth_header: dict
):
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
    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

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
@pytest.mark.asyncio
async def test_create_record_response_with_wrong_response_value(
    async_client: "AsyncClient",
    owner_auth_header: dict,
    create_questions_func: Callable[["Dataset"], None],
    responses: dict,
    expected_error_msg: str,
):
    dataset = await DatasetFactory.create()
    await create_questions_func(dataset)
    record = await RecordFactory.create(dataset=dataset)

    response_json = {**responses, "status": "submitted"}
    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    assert response.status_code == 422
    assert response.json() == {"detail": expected_error_msg}


@pytest.mark.asyncio
async def test_create_record_response_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    record = await RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = await async_client.post(f"/api/v1/records/{record.id}/responses", json=response_json)

    assert response.status_code == 401
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.parametrize("status", ["submitted", "discarded", "draft"])
@pytest.mark.asyncio
async def test_create_record_response(
    async_client: "AsyncClient", db: "AsyncSession", owner: User, owner_auth_header: dict, status: str
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

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

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
        "user_id": str(owner.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


@pytest.mark.parametrize(
    "status, expected_status_code, expected_response_count",
    [("submitted", 422, 0), ("discarded", 201, 1), ("draft", 422, 0)],
)
@pytest.mark.asyncio
async def test_create_record_response_without_values(
    async_client: "AsyncClient",
    db: "AsyncSession",
    owner: User,
    owner_auth_header: dict,
    status: str,
    expected_status_code: int,
    expected_response_count: int,
):
    record = await RecordFactory.create()
    response_json = {"status": status}

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    assert response.status_code == expected_status_code
    assert (await db.execute(select(func.count(Response.id)))).scalar() == expected_response_count

    if expected_status_code == 201:
        response_body = response.json()
        assert await db.get(Response, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "values": None,
            "status": "discarded",
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }


@pytest.mark.parametrize("status", ["submitted", "discarded", "draft"])
@pytest.mark.asyncio
async def test_create_record_submitted_response_with_wrong_values(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, status: str
):
    record = await RecordFactory.create()
    response_json = {"status": status, "values": {"wrong_question": {"value": "wrong value"}}}

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Error: found responses for non configured questions: ['wrong_question']"}
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_create_record_response_for_user_role(async_client: "AsyncClient", db: Session, role: UserRole):
    dataset = await DatasetFactory.create()
    await TextQuestionFactory.create(name="input_ok", dataset=dataset)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)

    record = await RecordFactory.create(dataset=dataset)
    user = await UserFactory.create(workspaces=[record.dataset.workspace], role=role)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: user.api_key}, json=response_json
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
        "user_id": str(user.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_create_record_response_as_restricted_user_from_different_workspace(
    async_client: "AsyncClient", db: Session, role: UserRole
):
    record = await RecordFactory.create()
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(workspaces=[workspace], role=role)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: user.api_key}, json=response_json
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_record_response_already_created(
    async_client: "AsyncClient", db: "AsyncSession", owner: User, owner_auth_header: dict
):
    record = await RecordFactory.create()
    await ResponseFactory.create(record=record, user=owner)
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    assert response.status_code == 409
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_record_response_with_invalid_values(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    record = await RecordFactory.create()
    response_json = {
        "values": "invalid",
        "status": "submitted",
    }

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_record_response_with_invalid_status(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    record = await RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "invalid",
    }

    response = await async_client.post(
        f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
    )

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_record_response_with_nonexistent_record_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    await RecordFactory.create()
    response_json = {
        "values": {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        "status": "submitted",
    }

    response = await async_client.post(
        f"/api/v1/records/{uuid4()}/responses", headers=owner_auth_header, json=response_json
    )

    assert response.status_code == 404
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_get_record_suggestions(async_client: "AsyncClient", role: UserRole):
    dataset = await DatasetFactory.create()
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])
    record = await RecordFactory.create(dataset=dataset)
    question_a = await TextQuestionFactory.create(dataset=dataset)
    question_b = await TextQuestionFactory.create(dataset=dataset)
    suggestion_a = await SuggestionFactory.create(
        question=question_a, record=record, value="This is a unit test suggestion"
    )
    suggestion_b = await SuggestionFactory.create(
        question=question_b, record=record, value="This is a another unit test suggestion"
    )

    response = await async_client.get(
        f"/api/v1/records/{record.id}/suggestions", headers={API_KEY_HEADER_NAME: user.api_key}
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(suggestion_a.id),
                "question_id": str(question_a.id),
                "type": None,
                "score": None,
                "value": "This is a unit test suggestion",
                "agent": None,
            },
            {
                "id": str(suggestion_b.id),
                "question_id": str(question_b.id),
                "type": None,
                "score": None,
                "value": "This is a another unit test suggestion",
                "agent": None,
            },
        ]
    }


@pytest.mark.parametrize(
    "payload",
    [
        {
            "type": "model",
            "score": 1,
            "value": "This is a unit test suggestion",
            "agent": "unit-test-agent",
        },
        {
            "type": None,
            "score": None,
            "value": "This is a unit test suggestion",
            "agent": None,
        },
    ],
)
@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_create_record_suggestion(async_client: "AsyncClient", db: "AsyncSession", role: UserRole, payload: dict):
    dataset = await DatasetFactory.create()
    question = await TextQuestionFactory.create(dataset=dataset)
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])
    record = await RecordFactory.create(dataset=dataset)

    response = await async_client.put(
        f"/api/v1/records/{record.id}/suggestions",
        headers={API_KEY_HEADER_NAME: user.api_key},
        json={"question_id": str(question.id), **payload},
    )

    response_body = response.json()
    assert response.status_code == 201
    assert response_body == {"id": response_body["id"], "question_id": str(question.id), **payload}
    assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_record_suggestion_update(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    dataset = await DatasetFactory.create()
    question = await TextQuestionFactory.create(dataset=dataset)
    record = await RecordFactory.create(dataset=dataset)
    suggestion = await SuggestionFactory.create(question=question, record=record)

    response = await async_client.put(
        f"/api/v1/records/{record.id}/suggestions",
        headers=owner_auth_header,
        json={"question_id": str(question.id), "value": "Testing updating a suggestion"},
    )

    response_body = response.json()
    assert response.status_code == 200
    assert response_body == {
        "id": str(suggestion.id),
        "question_id": str(question.id),
        "type": None,
        "score": None,
        "value": "Testing updating a suggestion",
        "agent": None,
    }
    assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 1


@pytest.mark.parametrize(
    "payload",
    [
        {},  # missing value
        {
            "value": {"this": "is not valid response for a TextQuestion"},
        },
    ],
)
@pytest.mark.asyncio
async def test_create_record_suggestion_not_valid(async_client: "AsyncClient", owner_auth_header: dict, payload: dict):
    dataset = await DatasetFactory.create()
    question = await TextQuestionFactory.create(dataset=dataset)
    record = await RecordFactory.create(dataset=dataset)

    response = await async_client.put(
        f"/api/v1/records/{record.id}/suggestions",
        headers=owner_auth_header,
        json={"question_id": str(question.id), **payload},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_record_suggestion_for_non_existent_question(async_client: "AsyncClient", owner_auth_header: dict):
    record = await RecordFactory.create()

    response = await async_client.put(
        f"/api/v1/records/{record.id}/suggestions",
        headers=owner_auth_header,
        json={"question_id": str(uuid4()), "value": "This is a unit test suggestion"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_record_suggestion_as_annotator(async_client: "AsyncClient"):
    annotator = await UserFactory.create(role=UserRole.annotator)
    record = await RecordFactory.create()

    response = await async_client.put(
        f"/api/v1/records/{record.id}/suggestions",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
        json={"question_id": str(uuid4()), "value": "This is a unit test suggestion"},
    )

    assert response.status_code == 403


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete_record(
    async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: "SearchEngine", role: UserRole
):
    dataset = await DatasetFactory.create()
    record = await RecordFactory.create(dataset=dataset)
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    response = await async_client.delete(f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200
    assert response.json() == {
        "id": str(record.id),
        "fields": record.fields,
        "metadata": None,
        "external_id": record.external_id,
        "inserted_at": record.inserted_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }
    assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
    mock_search_engine.delete_records.assert_called_once_with(dataset=dataset, records=[record])


@pytest.mark.asyncio
async def test_delete_record_as_admin_from_another_workspace(async_client: "AsyncClient", db: "AsyncSession"):
    dataset = await DatasetFactory.create()
    record = await RecordFactory.create(dataset=dataset)
    user = await UserFactory.create(role=UserRole.admin)

    response = await async_client.delete(f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Record.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_record_as_annotator(async_client: "AsyncClient"):
    annotator = await UserFactory.create(role=UserRole.annotator)
    record = await RecordFactory.create()

    response = await async_client.delete(
        f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_record_non_existent(async_client: "AsyncClient", owner_auth_header: dict):
    response = await async_client.delete(f"/api/v1/records/{uuid4()}", headers=owner_auth_header)
    assert response.status_code == 404
