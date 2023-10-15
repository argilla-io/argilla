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
from argilla.client import api
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.sdk.users.models import UserRole

from tests.factories import (
    DatasetFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestSuiteRemoteMetadataProperties:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete(self, role: UserRole, db: "AsyncSession") -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await TermsMetadataPropertyFactory.create(dataset=dataset)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key, workspace=dataset.workspace.name)

        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        assert remote_dataset.metadata_properties is not None
        assert len(remote_dataset.metadata_properties) == 1

        remote_dataset.metadata_properties[0].delete()
        await db.refresh(dataset, attribute_names=["metadata_properties"])
        assert len(remote_dataset.metadata_properties) == 0
