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
from argilla import (
    FeedbackRecord,
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
    TextField,
    TextQuestion,
)
from argilla.client import api
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
from argilla.client.sdk.users.models import UserRole
from argilla.client.workspaces import Workspace
from argilla.server.models import User as ServerUser
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    ResponseFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedMetadataPropertyTypes, AllowedRemoteMetadataPropertyTypes
    from argilla.client.sdk.users.models import UserModel as User


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
class TestRemoteFeedbackDataset:
    @pytest.mark.parametrize(
        "record",
        [
            FeedbackRecord(fields={"text": "Hello world!"}, metadata={}),
            FeedbackRecord(fields={"text": "Hello world!", "optional": "Bye world!"}, metadata={}),
            FeedbackRecord(fields={"text": "Hello world!"}, metadata={"terms-metadata": "a"}),
            FeedbackRecord(fields={"text": "Hello world!"}, metadata={"unrelated-metadata": "unrelated-value"}),
        ],
    )
    async def test_add_records(self, owner: "User", test_dataset: FeedbackDataset, record: FeedbackRecord) -> None:
        api.init(api_key=owner.api_key)
        ws = Workspace.create(name="test-workspace")

        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)

        remote_dataset = FeedbackDataset.from_argilla(id=remote.id)
        remote_dataset.add_records([record])

        assert len(remote_dataset.records) == 1

    @pytest.mark.parametrize(
        "metadata_property, remote_metadata_property_cls",
        [
            (TermsMetadataProperty(name="new-terms-metadata"), RemoteTermsMetadataProperty),
            (TermsMetadataProperty(name="new-terms-metadata", values=["a", "b", "c"]), RemoteTermsMetadataProperty),
            (IntegerMetadataProperty(name="new-integer-metadata"), RemoteIntegerMetadataProperty),
            (IntegerMetadataProperty(name="new-integer-metadata", min=0, max=10), RemoteIntegerMetadataProperty),
            (FloatMetadataProperty(name="new-float-metadata"), RemoteFloatMetadataProperty),
            (FloatMetadataProperty(name="new-float-metadata", min=0, max=10), RemoteFloatMetadataProperty),
        ],
    )
    async def test_add_metadata_property(
        self,
        owner: "User",
        metadata_property: "AllowedMetadataPropertyTypes",
        remote_metadata_property_cls: "AllowedRemoteMetadataPropertyTypes",
    ) -> None:
        dataset = await DatasetFactory.create(status="ready")
        await TextFieldFactory.create(dataset=dataset, name="required", required=True)
        await TextFieldFactory.create(dataset=dataset, name="optional", required=False)
        await TextQuestionFactory.create(dataset=dataset, required=True)

        api.init(api_key=owner.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        remote_metadata_property = remote_dataset.add_metadata_property(metadata_property)
        assert isinstance(remote_metadata_property, remote_metadata_property_cls)
        assert remote_metadata_property.name == metadata_property.name
        assert remote_dataset.metadata_properties == [remote_metadata_property]

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
    async def test_delete_records(self, owner: "User", role: UserRole, test_dataset: FeedbackDataset) -> None:
        user = await UserFactory.create(role=role)

        api.init(api_key=owner.api_key)
        ws = Workspace.create(name="test-workspace")
        ws.add_user(user.id)

        api.init(api_key=user.api_key, workspace=ws.name)

        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)
        remote.add_records(
            [
                FeedbackRecord(fields={"text": "Hello world!"}),
                FeedbackRecord(fields={"text": "Hello world!"}),
            ]
        )

        remote_records = [record for record in remote.records]
        assert all(record.id for record in remote_records)

        remote.delete_records(remote_records[0])
        assert len(remote.records) == len(remote_records) - 1

        remote.delete_records(remote_records[1:])
        assert len(remote.records) == 0

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete(self, owner: "User", test_dataset: FeedbackDataset, role: UserRole) -> None:
        user = await UserFactory.create(role=role)

        api.init(api_key=owner.api_key)

        ws = Workspace.create(name="test-workspace")
        ws.add_user(user.id)

        api.init(api_key=user.api_key)
        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)
        remote_dataset = FeedbackDataset.from_argilla(id=remote.id)
        remote_dataset.delete()

        with pytest.raises(Exception, match="Could not find a `FeedbackDataset` in Argilla"):
            FeedbackDataset.from_argilla(id=remote.id)

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
        await TermsMetadataPropertyFactory.create_batch(dataset=dataset, size=10)
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
        await TermsMetadataPropertyFactory.create_batch(dataset=dataset, size=10)
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
        await TermsMetadataPropertyFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)

        assert isinstance(remote_dataset.id, UUID)
        assert isinstance(remote_dataset.name, str)
        assert isinstance(remote_dataset.workspace, Workspace)
        assert isinstance(remote_dataset.url, str)
        assert isinstance(remote_dataset.created_at, datetime)
        assert isinstance(remote_dataset.updated_at, datetime)

    async def test_pull_without_results(
        self,
        argilla_user: ServerUser,
        feedback_dataset_guidelines: str,
        feedback_dataset_fields: List[AllowedFieldTypes],
        feedback_dataset_questions: List[AllowedQuestionTypes],
        feedback_dataset_records: List[FeedbackRecord],
        db: AsyncSession,
    ) -> None:
        api.active_api()
        api.init(api_key=argilla_user.api_key)

        dataset = FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )
        dataset.push_to_argilla(name="test-dataset")

        await db.refresh(argilla_user, attribute_names=["datasets"])

        same_dataset = FeedbackDataset.from_argilla("test-dataset")
        local_copy = same_dataset.pull()

        assert local_copy is not None
        assert local_copy.records == []
