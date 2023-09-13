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
from uuid import UUID

import pytest
from argilla.client import api
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.sdk.users.models import UserRole
from argilla.client.workspaces import Workspace

from tests.factories import DatasetFactory, RecordFactory, TextFieldFactory, TextQuestionFactory, UserFactory


@pytest.mark.asyncio
class TestRemoteFeedbackDataset:
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

    @pytest.mark.parametrize("role", [UserRole.owner])
    async def test_not_implemented_methods(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        ds = FeedbackDataset.from_argilla(id=dataset.id)

        with pytest.warns(
            match="`prepare_for_training` is not implemented for `RemoteFeedbackDataset`. First call `pull_from_argilla` to get a local instance of the dataset, and then call `prepare_for_training` on that instance."
        ):
            ds.prepare_for_training()

        with pytest.warns(
            match="`push_to_argilla` doesn't work for neither `RemoteFeedbackDataset` nor `FilteredRemoteFeedbackDataset`,"
        ):
            ds.push_to_argilla()
