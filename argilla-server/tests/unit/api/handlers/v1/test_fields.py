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
from argilla_server.api.schemas.v1.fields import FIELD_CREATE_TITLE_MAX_LENGTH
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import DatasetStatus, Field, UserRole
from sqlalchemy import func, select

from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    TextFieldFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.parametrize(
    "payload, expected_settings",
    [
        (
            {"title": "New Title", "settings": {"type": "text", "use_markdown": True}},
            {"type": "text", "use_markdown": True},
        ),
        ({"title": "New Title"}, {"type": "text", "use_markdown": False}),
        (
            {"name": "New Name", "required": True, "dataset_id": str(uuid4())},
            {"type": "text", "use_markdown": False},
        ),
    ],
)
@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_update_field(
    async_client: "AsyncClient", db: "AsyncSession", role: UserRole, payload: dict, expected_settings: dict
):
    field = await TextFieldFactory.create()
    user = await UserFactory.create(role=role, workspaces=[field.dataset.workspace])

    response = await async_client.patch(
        f"/api/v1/fields/{field.id}", headers={API_KEY_HEADER_NAME: user.api_key}, json=payload
    )

    title = payload.get("title") or field.title

    assert response.status_code == 200
    assert response.json() == {
        "id": str(field.id),
        "name": field.name,
        "title": title,
        "required": field.required,
        "settings": expected_settings,
        "dataset_id": str(field.dataset.id),
        "inserted_at": field.inserted_at.isoformat(),
        "updated_at": field.updated_at.isoformat(),
    }

    field = await db.get(Field, field.id)
    assert field.title == title
    assert field.settings == expected_settings


@pytest.mark.parametrize("title", [None, "", "t" * (FIELD_CREATE_TITLE_MAX_LENGTH + 1)])
@pytest.mark.asyncio
async def test_update_field_with_invalid_title(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, title: str
):
    field = await TextFieldFactory.create(title="title")

    response = await async_client.patch(f"/api/v1/fields/{field.id}", headers=owner_auth_header, json={"title": title})

    assert response.status_code == 422

    field = await db.get(Field, field.id)
    assert field.title == "title"


@pytest.mark.parametrize(
    "payload",
    [
        {"settings": None},
        {"settings": {"type": "text"}},
        {"settings": {"type": "text", "use_markdown": None}},
        {"settings": {"type": "i don't exist"}},
    ],
)
@pytest.mark.asyncio
async def test_update_field_with_invalid_settings(async_client: "AsyncClient", owner_auth_header: dict, payload: dict):
    field = await TextFieldFactory.create()

    response = await async_client.patch(f"/api/v1/fields/{field.id}", headers=owner_auth_header, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_field_with_invalid_payload(async_client: "AsyncClient", owner_auth_header: dict):
    field = await TextFieldFactory.create()

    response = await async_client.patch(
        f"/api/v1/fields/{field.id}",
        headers=owner_auth_header,
        json={"title": {"this": "is", "not": "valid"}, "settings": {"use_markdown": "no"}},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_field_non_existent(async_client: "AsyncClient", owner_auth_header: dict):
    field_id = uuid4()

    response = await async_client.patch(
        f"/api/v1/fields/{field_id}",
        headers=owner_auth_header,
        json={"title": "New Title", "settings": {"type": "text", "use_markdown": True}},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Field with id `{field_id}` not found"}


@pytest.mark.asyncio
async def test_update_field_as_admin_from_different_workspace(async_client: "AsyncClient"):
    field = await TextFieldFactory.create()
    user = await UserFactory.create(role=UserRole.admin)

    response = await async_client.patch(
        f"/api/v1/fields/{field.id}",
        headers={API_KEY_HEADER_NAME: user.api_key},
        json={"title": "New Title", "settings": {"type": "text", "use_markdown": True}},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_field_as_annotator(async_client: "AsyncClient"):
    field = await TextFieldFactory.create()
    user = await UserFactory.create(role=UserRole.annotator, workspaces=[field.dataset.workspace])

    response = await async_client.patch(
        f"/api/v1/fields/{field.id}",
        headers={API_KEY_HEADER_NAME: user.api_key},
        json={"title": "New Title", "settings": {"type": "text", "use_markdown": True}},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_field_without_authentication(async_client: "AsyncClient"):
    field = await TextFieldFactory.create()

    response = await async_client.patch(
        f"/api/v1/fields/{field.id}",
        json={"title": "New Title", "settings": {"use_markdown": True}},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_field(async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict):
    field = await TextFieldFactory.create(name="name", title="title")

    response = await async_client.delete(f"/api/v1/fields/{field.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

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


@pytest.mark.asyncio
async def test_delete_field_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    field = await TextFieldFactory.create()

    response = await async_client.delete(f"/api/v1/fields/{field.id}")

    assert response.status_code == 401
    assert (await db.execute(select(func.count(Field.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_field_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    field = await TextFieldFactory.create()

    response = await async_client.delete(f"/api/v1/fields/{field.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Field.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_field_belonging_to_published_dataset(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    dataset = await DatasetFactory.create(status=DatasetStatus.ready)
    field = await TextFieldFactory.create(dataset=dataset)

    response = await async_client.delete(f"/api/v1/fields/{field.id}", headers=owner_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Fields cannot be deleted for a published dataset"}

    assert (await db.execute(select(func.count(Field.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_field_with_nonexistent_field_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    field_id = uuid4()

    await TextFieldFactory.create()

    response = await async_client.delete(f"/api/v1/fields/{field_id}", headers=owner_auth_header)

    assert response.status_code == 404
    assert response.json() == {"detail": f"Field with id `{field_id}` not found"}

    assert (await db.execute(select(func.count(Field.id)))).scalar() == 1
