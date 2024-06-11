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

from typing import TYPE_CHECKING

import pytest
from argilla_server.models import UserRole
from argilla_v1.client.client import Argilla
from argilla_v1.client.sdk.v1.metadata_properties.api import delete_metadata_property, update_metadata_property

from tests.factories import (
    DatasetFactory,
    FloatMetadataPropertyFactory,
    IntegerMetadataPropertyFactory,
    TermsMetadataPropertyFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestSuiteMetadataPropertiesSDK:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_metadata_property(self, role: UserRole, db: "AsyncSession") -> None:
        dataset = await DatasetFactory.create()
        await TermsMetadataPropertyFactory.create(dataset=dataset)
        await FloatMetadataPropertyFactory.create(dataset=dataset)
        await IntegerMetadataPropertyFactory.create(dataset=dataset)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

        await db.refresh(dataset, attribute_names=["metadata_properties"])
        assert len(dataset.metadata_properties) == 3

        for metadata_property in dataset.metadata_properties:
            response = delete_metadata_property(client=api.client.httpx, id=metadata_property.id)
            assert response.status_code == 200
            assert response.parsed.id == metadata_property.id

        await db.refresh(dataset, attribute_names=["metadata_properties"])
        assert len(dataset.metadata_properties) == 0

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_update_metadata_property(self, role: UserRole, db: "AsyncSession") -> None:
        dataset = await DatasetFactory.create()
        await TermsMetadataPropertyFactory.create(dataset=dataset)
        await FloatMetadataPropertyFactory.create(dataset=dataset)
        await IntegerMetadataPropertyFactory.create(dataset=dataset)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

        await db.refresh(dataset, attribute_names=["metadata_properties"])
        assert len(dataset.metadata_properties) == 3

        for metadata_property in dataset.metadata_properties:
            response = update_metadata_property(
                client=api.client.httpx, id=metadata_property.id, title="new-title", visible_for_annotators=False
            )
            assert response.status_code == 200
            assert response.parsed.title == "new-title"
            assert response.parsed.visible_for_annotators is False

        await db.refresh(dataset, attribute_names=["metadata_properties"])
        assert len(dataset.metadata_properties) == 3
        for metadata_property in dataset.metadata_properties:
            assert metadata_property.title == "new-title"
            assert metadata_property.visible_for_annotators is False
