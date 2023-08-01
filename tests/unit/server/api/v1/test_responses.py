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
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import DatasetStatus, Response, ResponseStatus, UserRole
from argilla.server.search_engine import SearchEngine
from sqlalchemy import func, select

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

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_update_response(
    async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine, owner_auth_header: dict
):
    dataset = await DatasetFactory.create(status=DatasetStatus.ready)
    await TextQuestionFactory.create(name="input_ok", dataset=dataset)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)
    record = await RecordFactory.create(dataset=dataset)

    response = await ResponseFactory.create(
        record=record,
        values={"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
        status=ResponseStatus.submitted,
    )
    response_json = {
        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
        "status": "submitted",
    }

    resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 200
    assert (await db.get(Response, response.id)).values == {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}}

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


@pytest.mark.asyncio
async def test_update_response_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    response = await ResponseFactory.create(
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

    resp = await async_client.put(f"/api/v1/responses/{response.id}", json=response_json)

    assert resp.status_code == 401
    assert (await db.get(Response, response.id)).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


@pytest.mark.asyncio
async def test_update_response_from_submitted_to_discarded(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    dataset = await DatasetFactory.create(status=DatasetStatus.ready)
    await TextQuestionFactory.create(name="input_ok", dataset=dataset)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)
    record = await RecordFactory.create(dataset=dataset)

    response = await ResponseFactory.create(
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

    resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 200

    response = await db.get(Response, response.id)
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


@pytest.mark.asyncio
async def test_update_response_from_submitted_to_discarded_without_values(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    response = await ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        status="submitted",
    )
    response_json = {
        "status": "discarded",
    }

    resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 200

    response = await db.get(Response, response.id)
    assert response.values is None
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


@pytest.mark.asyncio
async def test_update_response_from_discarded_to_submitted(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    response = await ResponseFactory.create(status="discarded")
    response_json = {
        "status": "submitted",
    }

    resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_response_from_discarded_to_submitted_without_values(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    response = await ResponseFactory.create(status="discarded")
    response_json = {
        "status": "submitted",
    }

    resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 422

    response = await db.get(Response, response.id)
    assert response.values is None
    assert response.status == ResponseStatus.discarded


@pytest.mark.asyncio
async def test_update_response_with_wrong_values(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    response = await ResponseFactory.create(status="discarded")
    response_json = {"status": "submitted", "values": {"wrong_question": {"value": "wrong value"}}}

    resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 422
    assert resp.json() == {"detail": "Error: found responses for non configured questions: ['wrong_question']"}

    response = await db.get(Response, response.id)
    assert response.values is None
    assert response.status == ResponseStatus.discarded


@pytest.mark.asyncio
async def test_update_response_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    dataset = await DatasetFactory.create(status=DatasetStatus.ready)
    await TextQuestionFactory.create(name="input_ok", dataset=dataset)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)
    record = await RecordFactory.create(dataset=dataset)
    annotator = await AnnotatorFactory.create()

    response = await ResponseFactory.create(
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

    resp = await async_client.put(
        f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
    )

    assert resp.status_code == 200
    assert (await db.get(Response, response.id)).values == {
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


@pytest.mark.asyncio
async def test_update_response_as_annotator_for_different_user_response(
    async_client: "AsyncClient", db: "AsyncSession"
):
    annotator = await AnnotatorFactory.create()
    response = await ResponseFactory.create(
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

    resp = await async_client.put(
        f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
    )

    assert resp.status_code == 403
    assert (await db.get(Response, response.id)).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


@pytest.mark.asyncio
async def test_update_response_with_nonexistent_response_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    response = await ResponseFactory.create(
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

    resp = await async_client.put(f"/api/v1/responses/{uuid4()}", headers=owner_auth_header, json=response_json)

    assert resp.status_code == 404
    assert (await db.get(Response, response.id)).values == {
        "input_ok": {"value": "no"},
        "output_ok": {"value": "no"},
    }


@pytest.mark.asyncio
async def test_delete_response(
    async_client: "AsyncClient", mock_search_engine: SearchEngine, db: "AsyncSession", owner_auth_header: dict
):
    response = await ResponseFactory.create()

    resp = await async_client.delete(f"/api/v1/responses/{response.id}", headers=owner_auth_header)

    assert resp.status_code == 200
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    mock_search_engine.delete_record_response.assert_called_once_with(response)


@pytest.mark.asyncio
async def test_delete_response_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    response = await ResponseFactory.create()

    resp = await async_client.delete(f"/api/v1/responses/{response.id}")

    assert resp.status_code == 401
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_delete_response_as_restricted_user(async_client: "AsyncClient", db: "AsyncSession", role: UserRole):
    user = await UserFactory.create(role=role)
    response = await ResponseFactory.create(user=user)

    resp = await async_client.delete(f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: user.api_key})

    assert resp.status_code == 200
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_delete_response_as_admin_for_different_user_response(async_client: "AsyncClient", db: "AsyncSession"):
    workspace = await WorkspaceFactory.create()
    admin = await AdminFactory.create(workspaces=[workspace])
    dataset = await DatasetFactory.create(workspace=workspace)
    record = await RecordFactory.create(dataset=dataset)
    response = await ResponseFactory.create(record=record)

    resp = await async_client.delete(f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert resp.status_code == 200
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_delete_response_as_annotator_for_different_user_response(
    async_client: "AsyncClient", db: "AsyncSession"
):
    annotator = await AnnotatorFactory.create()
    response = await ResponseFactory.create()

    resp = await async_client.delete(
        f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert resp.status_code == 403
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_response_with_nonexistent_response_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    await ResponseFactory.create()

    resp = await async_client.delete(f"/api/v1/responses/{uuid4()}", headers=owner_auth_header)

    assert resp.status_code == 404
    assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
