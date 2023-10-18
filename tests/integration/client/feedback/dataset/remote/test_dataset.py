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
from typing import TYPE_CHECKING, List
from uuid import UUID

import pytest
from argilla.client import api
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.sdk.users.models import UserRole
from argilla.client.workspaces import Workspace

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from argilla.client.sdk.users.models import UserModel as User


@pytest.mark.asyncio
class TestRemoteFeedbackDataset:
    @pytest.mark.parametrize("statuses", [["draft", "discarded", "submitted"]])
    async def test_from_argilla_with_responses(self, owner: "User", statuses: List[str]) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        text_question = await TextQuestionFactory.create(dataset=dataset, required=True)
        for status, record in zip(statuses, await RecordFactory.create_batch(size=len(statuses), dataset=dataset)):
            await ResponseFactory.create(record=record, values={text_question.name: {"value": ""}}, status=status)

        api.init(api_key=owner.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        assert remote_dataset.id == dataset.id
        assert all(
            status in [response.status for record in remote_dataset.records for response in record.responses]
            for status in statuses
        )

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_records(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
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
    async def test_delete(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        remote_dataset.delete()

        datasets = api.active_api().http_client.get("/api/v1/me/datasets")["items"]
        assert not any(ds["name"] == remote_dataset.name for ds in datasets)

    @pytest.mark.parametrize("role", [UserRole.annotator])
    async def test_delete_not_allowed_role(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)

        with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `delete`"):
            remote_dataset.delete()

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
    async def test_list(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_datasets = FeedbackDataset.list()
        assert len(remote_datasets) == 1
        assert all(isinstance(remote_dataset, RemoteFeedbackDataset) for remote_dataset in remote_datasets)
        assert all(remote_dataset.workspace.id == dataset.workspace.id for remote_dataset in remote_datasets)

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
    async def test_list_with_workspace_name(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_datasets = FeedbackDataset.list(workspace=dataset.workspace.name)
        assert len(remote_datasets) == 1
        assert all(isinstance(remote_dataset, RemoteFeedbackDataset) for remote_dataset in remote_datasets)
        assert all(remote_dataset.workspace.id == dataset.workspace.id for remote_dataset in remote_datasets)

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_attributes(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)

        assert isinstance(remote_dataset.id, UUID)
        assert isinstance(remote_dataset.name, str)
        assert isinstance(remote_dataset.workspace, Workspace)
        assert isinstance(remote_dataset.url, str)
        assert isinstance(remote_dataset.created_at, datetime)
        assert isinstance(remote_dataset.updated_at, datetime)

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_warning_local_methods(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        ds = FeedbackDataset.from_argilla(id=dataset.id)

        with pytest.raises(ValueError, match="`FeedbackRecord.fields` does not match the expected schema"):
            with pytest.warns(
                UserWarning,
                match="A local `FeedbackDataset` returned because `unify_responses` is not supported for `RemoteFeedbackDataset`. ",
            ):
                ds.unify_responses(question=None, strategy=None)

        with pytest.raises(ValueError, match="`FeedbackRecord.fields` does not match the expected schema"):
            with pytest.warns(
                UserWarning,
                match="A local `FeedbackDataset` returned because `prepare_for_training` is not supported for `RemoteFeedbackDataset`. ",
            ):
                ds.prepare_for_training(framework=None, task=None)
