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
from argilla_v1 import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
    TextField,
    TextQuestion,
    Workspace,
)
from argilla_v1.client import singleton
from argilla_v1.client.feedback.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas.records import FeedbackRecord, SuggestionSchema
from argilla_v1.client.feedback.schemas.remote.records import RemoteFeedbackRecord, RemoteSuggestionSchema
from argilla_v1.client.sdk.users.models import UserRole

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    SuggestionFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture()
def test_dataset():
    dataset = FeedbackDataset(
        fields=[TextField(name="text"), TextField(name="optional", required=False)],
        questions=[TextQuestion(name="question")],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="integer-metadata"),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    return dataset


@pytest.mark.asyncio
class TestSuiteRemoteFeedbackRecord:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete(self, owner: "User", test_dataset: FeedbackDataset, role: UserRole) -> None:
        user = await UserFactory.create(role=role)

        singleton.init(api_key=owner.api_key)

        ws = Workspace.create(name="test-workspace")
        ws.add_user(user.id)

        singleton.init(api_key=user.api_key)
        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)
        remote_dataset = FeedbackDataset.from_argilla(id=remote.id)
        remote.add_records(
            [
                FeedbackRecord(fields={"text": "Hello world!"}),
                FeedbackRecord(fields={"text": "Hello world!"}),
            ]
        )

        remote_records = [record for record in remote_dataset.records]
        assert all(isinstance(record, RemoteFeedbackRecord) for record in remote_records)

        deleted_records = []
        for record in remote_records:
            deleted_records.append(record.delete())
        assert all(isinstance(record, FeedbackRecord) for record in deleted_records)
        assert len(remote_dataset.records) == 0

    @pytest.mark.skip(reason="Enable when factories are removed from the test")
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_update(self, role: UserRole, db: "AsyncSession") -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        question = await TextQuestionFactory.create(dataset=dataset, required=True)
        records = await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        singleton.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        remote_records = [record for record in remote_dataset.records]
        assert all(isinstance(record, RemoteFeedbackRecord) for record in remote_records)
        assert all(record.suggestions == () for record in remote_records)

        suggestion = SuggestionSchema(
            question_name=question.name,
            value="suggestion",
        )
        for remote_record, factory_record in zip(remote_records, records):
            remote_record.update(suggestions=[suggestion])
            await db.refresh(factory_record, attribute_names=["suggestions"])
        assert all(
            isinstance(suggestion, RemoteSuggestionSchema)
            for remote_record in remote_records
            for suggestion in remote_record.suggestions
        )

    @pytest.mark.skip(reason="Enable when factories are removed from the test")
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_suggestions(self, role: UserRole, db: "AsyncSession") -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        question = await TextQuestionFactory.create(dataset=dataset, required=True)
        record = await RecordFactory.create(dataset=dataset)
        await SuggestionFactory.create(record=record, question=question)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        singleton.init(api_key=user.api_key, workspace=dataset.workspace.name)

        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        assert len(remote_dataset.records) == 1
        assert isinstance(remote_dataset.records[0], RemoteFeedbackRecord)
        assert all(
            isinstance(suggestion, RemoteSuggestionSchema) for suggestion in remote_dataset.records[0].suggestions
        )

        remote_dataset.records[0].delete_suggestions(remote_dataset.records[0].suggestions[0])
        await db.refresh(record, attribute_names=["suggestions"])
        assert len(remote_dataset.records[0].suggestions) == 0


@pytest.mark.asyncio
class TestSuiteRemoteSuggestionSchema:
    @pytest.mark.skip(reason="Enable when factories are removed from the test")
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete(self, role: UserRole, db: "AsyncSession") -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        question = await TextQuestionFactory.create(dataset=dataset, required=True)
        record = await RecordFactory.create(dataset=dataset)
        await SuggestionFactory.create(record=record, question=question)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        singleton.init(api_key=user.api_key, workspace=dataset.workspace.name)

        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        assert len(remote_dataset.records) == 1
        assert isinstance(remote_dataset.records[0], RemoteFeedbackRecord)
        assert all(
            isinstance(suggestion, RemoteSuggestionSchema) for suggestion in remote_dataset.records[0].suggestions
        )

        for suggestion in remote_dataset.records[0].suggestions:
            suggestion.delete()
        await db.refresh(record, attribute_names=["suggestions"])
        assert len(remote_dataset.records[0].suggestions) == 0
