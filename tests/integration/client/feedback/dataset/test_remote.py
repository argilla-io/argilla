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

import pytest
from argilla.client import api
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.sdk.users.models import UserRole

from tests.factories import DatasetFactory, RecordFactory, TextFieldFactory, TextQuestionFactory, UserFactory


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete_records(role: UserRole) -> None:
    text_field = await TextFieldFactory.create(required=True)
    rating_question = await TextQuestionFactory.create(required=True)
    dataset = await DatasetFactory.create(
        fields=[text_field],
        questions=[rating_question],
        records=RecordFactory.create_batch(size=10),
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api.init(api_key=user.api_key)
    remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
    remote_records = [record for record in remote_dataset.records]
    assert all(record.id for record in remote_records)

    remote_dataset.delete_records(remote_records[0])
    assert len(remote_dataset.records) == len(remote_records) - 1

    remote_dataset.delete_records(remote_records[1:])
    assert len(remote_dataset.records) == 0


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete(role: UserRole) -> None:
    text_field = await TextFieldFactory.create(required=True)
    rating_question = await TextQuestionFactory.create(required=True)
    dataset = await DatasetFactory.create(fields=[text_field], questions=[rating_question])
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api.init(api_key=user.api_key)
    remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
    remote_dataset.delete()

    datasets = api.active_api().http_client.get("/api/v1/me/datasets")["items"]
    assert not any(ds["name"] == remote_dataset.name for ds in datasets)


@pytest.mark.parametrize("role", [UserRole.annotator])
@pytest.mark.asyncio
async def test_delete_not_allowed_role(role: UserRole) -> None:
    text_field = await TextFieldFactory.create(required=True)
    rating_question = await TextQuestionFactory.create(required=True)
    dataset = await DatasetFactory.create(fields=[text_field], questions=[rating_question])
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api.init(api_key=user.api_key)
    remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)

    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `delete`"):
        remote_dataset.delete()
