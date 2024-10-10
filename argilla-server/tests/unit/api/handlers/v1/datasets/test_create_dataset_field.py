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
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select

from argilla_server.api.schemas.v1.fields import FIELD_CREATE_NAME_MAX_LENGTH, FIELD_CREATE_TITLE_MAX_LENGTH
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import (
    DatasetStatus,
)
from argilla_server.models import (
    Field,
)
from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    FieldFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestCreateDatasetField:
    @pytest.mark.parametrize(
        ("settings", "expected_settings"),
        [
            ({"type": "text"}, {"type": "text", "use_markdown": False}),
            ({"type": "text", "discarded": "value"}, {"type": "text", "use_markdown": False}),
            ({"type": "text", "use_markdown": False}, {"type": "text", "use_markdown": False}),
        ],
    )
    async def test_create_dataset_field(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        settings: dict,
        expected_settings: dict,
    ):
        dataset = await DatasetFactory.create()
        field_json = {"name": "name", "title": "title", "settings": settings}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 1

        response_body = response.json()
        assert await db.get(Field, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "name": "name",
            "title": "title",
            "required": False,
            "settings": expected_settings,
            "dataset_id": str(dataset.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    async def test_create_dataset_field_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(f"/api/v1/datasets/{dataset.id}/fields", json=field_json)

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=field_json,
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 1

    async def test_create_dataset_field_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json=field_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_invalid_max_length_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "a" * (FIELD_CREATE_NAME_MAX_LENGTH + 1),
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        # assert db.query(Field).count() == 0
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_invalid_max_length_title(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "a" * (FIELD_CREATE_TITLE_MAX_LENGTH + 1),
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "settings",
        [
            {},
            None,
            {"type": "wrong-type"},
            {"type": "text", "use_markdown": None},
            {"type": "rating", "options": None},
            {"type": "rating", "options": []},
        ],
    )
    async def test_create_dataset_field_with_invalid_settings(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, settings: dict
    ):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "Title",
            "settings": settings,
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_existent_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        field = await FieldFactory.create(name="name")

        response = await async_client.post(
            f"/api/v1/datasets/{field.dataset_id}/fields",
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {"type": "text"},
            },
        )

        assert response.status_code == 409
        assert response.json() == {
            "detail": f"Field with name `{field.name}` already exists for dataset with id `{field.dataset_id}`"
        }

        assert (await db.execute(select(func.count(Field.id)))).scalar() == 1

    async def test_create_dataset_field_with_published_dataset(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields",
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {"type": "text"},
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Field cannot be created for a published dataset"}

        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset_id = uuid4()

        await DatasetFactory.create()

        response = await async_client.post(
            f"/api/v1/datasets/{dataset_id}/fields",
            headers=owner_auth_header,
            json={
                "name": "text",
                "title": "Text",
                "settings": {"type": "text"},
            },
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Dataset with id `{dataset_id}` not found"}

        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0
