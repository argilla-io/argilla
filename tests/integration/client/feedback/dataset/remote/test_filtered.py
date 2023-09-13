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
from typing import List, Union
from uuid import UUID

import pytest
from argilla.client import api
from argilla.client.feedback.dataset.local import FeedbackDataset
from argilla.client.feedback.dataset.remote.filtered import FilteredRemoteFeedbackDataset, FilteredRemoteFeedbackRecords
from argilla.client.feedback.schemas.records import FeedbackRecord, RemoteFeedbackRecord
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.datasets.models import FeedbackResponseStatusFilter
from argilla.client.workspaces import Workspace

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
)


@pytest.mark.asyncio
class TestFilteredRemoteFeedbackDataset:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    @pytest.mark.parametrize(
        "status",
        [
            FeedbackResponseStatusFilter.draft,
            FeedbackResponseStatusFilter.missing,
            FeedbackResponseStatusFilter.discarded,
            FeedbackResponseStatusFilter.submitted,
            [FeedbackResponseStatusFilter.discarded, FeedbackResponseStatusFilter.submitted],
        ],
    )
    async def test_filter_by(
        self, role: UserRole, status: Union[FeedbackResponseStatusFilter, List[FeedbackResponseStatusFilter]]
    ) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        filtered_dataset = remote_dataset.filter_by(response_status=status)
        assert isinstance(filtered_dataset, FilteredRemoteFeedbackDataset)
        assert isinstance(filtered_dataset.records, FilteredRemoteFeedbackRecords)
        assert all([isinstance(record, RemoteFeedbackRecord) for record in filtered_dataset.records])

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    @pytest.mark.parametrize(
        "status",
        [
            FeedbackResponseStatusFilter.draft,
            FeedbackResponseStatusFilter.missing,
            FeedbackResponseStatusFilter.discarded,
            FeedbackResponseStatusFilter.submitted,
            [FeedbackResponseStatusFilter.discarded, FeedbackResponseStatusFilter.submitted],
        ],
    )
    async def test_not_implemented_methods(
        self, role: UserRole, status: Union[FeedbackResponseStatusFilter, List[FeedbackResponseStatusFilter]]
    ) -> None:
        dataset = await DatasetFactory.create()
        text_field = await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        filtered_dataset = remote_dataset.filter_by(response_status=status)
        assert isinstance(filtered_dataset, FilteredRemoteFeedbackDataset)

        with pytest.raises(NotImplementedError, match="`records.delete` does not work for filtered datasets."):
            filtered_dataset.delete_records(remote_dataset.records[0])

        with pytest.raises(NotImplementedError, match="`records.delete` does not work for filtered datasets."):
            filtered_dataset.records.delete(remote_dataset.records[0])

        with pytest.raises(NotImplementedError, match="`records.add` does not work for filtered datasets."):
            filtered_dataset.add_records(FeedbackRecord(fields={text_field.name: "test"}))

        with pytest.raises(NotImplementedError, match="`records.add` does not work for filtered datasets."):
            filtered_dataset.records.add(FeedbackRecord(fields={text_field.name: "test"}))

        with pytest.warns(
            match="`delete` does not work for filtered datasets. First call `filter_reset\(\)` and then `delete\(\)`."
        ):
            filtered_dataset.delete()

        with pytest.warns(match="Removing old filters and applying new ones."):
            filtered_dataset.filter_by()

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_attributes(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])
        await TextFieldFactory.create(dataset=dataset, required=True)
        question = await TextQuestionFactory.create(dataset=dataset, required=True)
        for record in await RecordFactory.create_batch(dataset=dataset, size=10):
            await ResponseFactory.create(
                record=record, user=user, values={question.name: {"value": ""}}, status="submitted"
            )

        api.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        filtered_dataset = remote_dataset.filter_by(response_status="submitted")

        assert isinstance(filtered_dataset.id, UUID)
        assert isinstance(filtered_dataset.name, str)
        assert isinstance(filtered_dataset.workspace, Workspace)
        assert isinstance(filtered_dataset.url, str)
        assert isinstance(filtered_dataset.created_at, datetime)
        assert isinstance(filtered_dataset.updated_at, datetime)
