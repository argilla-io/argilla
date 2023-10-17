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
from typing import TYPE_CHECKING, Any, List, Tuple, Type
from uuid import UUID

import argilla as rg
import pytest
from argilla import (
    FeedbackRecord,
)
from argilla.client import api
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas import SuggestionSchema
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
from argilla.client.sdk.commons.errors import ValidationApiError
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


@pytest.fixture
def feedback_dataset() -> FeedbackDataset:
    return FeedbackDataset(
        fields=[TextField(name="text"), TextField(name="text-2")],
        questions=[
            TextQuestion(name="text"),
            LabelQuestion(name="label", labels=["label-1", "label-2", "label-3"], required=False),
            MultiLabelQuestion(name="multi-label", labels=["label-1", "label-2", "label-3"], required=False),
            RankingQuestion(name="ranking", values=["top-1", "top-2", "top-3"], required=False),
            RatingQuestion(name="rating", values=[1, 2, 3, 4, 5], required=False),
        ],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="integer-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0, max=10),
        ],
        guidelines="unit test guidelines",
        allow_extra_metadata=False,
    )


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

    def test_update_records(self, owner: "User", test_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        ws = rg.Workspace.create(name="test-workspace")

        test_dataset.add_records(
            [
                FeedbackRecord(fields={"text": "Hello world!"}),
                FeedbackRecord(fields={"text": "Another record"}),
            ]
        )

        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)

        first_record = remote[0]
        first_record.external_id = "new-external-id"
        first_record.metadata.update({"terms-metadata": "a"})

        remote.update_records(first_record)
        print(first_record)

        assert first_record == remote[0]

        first_record = remote[0]
        assert first_record.metadata["terms-metadata"] == "a"
        assert first_record.external_id == "new-external-id"

    async def test_update_records_with_suggestions(self, owner: "User", test_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        ws = rg.Workspace.create(name="test-workspace")

        test_dataset.add_records(
            [
                FeedbackRecord(fields={"text": "Hello world!"}),
                FeedbackRecord(fields={"text": "Another record"}),
            ]
        )

        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)

        records = []
        for record in remote:
            record.suggestions = [
                SuggestionSchema(question_name="question", value=f"Hello world! for {record.fields['text']}")
            ]
            records.append(record)

        remote.update_records(records)

        for record in records:
            for suggestion in record.suggestions:
                assert suggestion.question_name == "question"
                assert suggestion.value == f"Hello world! for {record.fields['text']}"

    @pytest.mark.parametrize(
        "metadata", [("terms-metadata", "wrong-label"), ("integer-metadata", "wrong-integer"), ("float-metadata", 11.5)]
    )
    async def test_update_records_with_metadata_validation_error(
        self, owner: "User", test_dataset: FeedbackDataset, metadata: Tuple[str, Any]
    ):
        rg.init(api_key=owner.api_key)
        ws = rg.Workspace.create(name="test-workspace")

        test_dataset.add_records(FeedbackRecord(fields={"text": "Hello world!"}))

        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)

        key, value = metadata

        record = remote[0]
        record.metadata.update({key: value})

        with pytest.raises(ValueError, match=r"`FeedbackRecord.metadata` .* does not match the expected schema"):
            remote.update_records([record])

        record.metadata = {"new-metadata": 100}
        remote.update_records([record])

        remote.add_metadata_property(IntegerMetadataProperty(name="new-metadata", min=0, max=10))
        with pytest.raises(
            ValueError, match="Provided 'new-metadata=100' is not valid, only values between 0 and 10 are allowed."
        ):
            remote.update_records([record])

        with pytest.raises(ValidationApiError, match=r"'new-metadata' metadata property validation failed"):
            record.update()

    async def test_from_argilla(self, feedback_dataset: FeedbackDataset, owner: "User") -> None:
        api.init(api_key=owner.api_key)
        workspace = Workspace.create(name="unit-test")

        remote = feedback_dataset.push_to_argilla(name="unit-test-dataset", workspace="unit-test")

        assert remote.name == "unit-test-dataset"
        assert remote.workspace.name == workspace.name
        assert remote.guidelines == "unit test guidelines"
        assert remote.allow_extra_metadata is False

        for remote_field, field in zip(remote.fields, feedback_dataset.fields):
            assert field.name == remote_field.name
            assert field.type == remote_field.type
            assert field.required == remote_field.required

        for remote_question, question in zip(remote.questions, feedback_dataset.questions):
            assert question.name == remote_question.name
            assert question.type == remote_question.type
            assert question.required == remote_question.required

        for remote_metadata_property, metadata_property in zip(
            remote.metadata_properties, feedback_dataset.metadata_properties
        ):
            assert metadata_property.name == remote_metadata_property.name
            assert metadata_property.type == remote_metadata_property.type

        remote = FeedbackDataset.from_argilla(id=remote.id)

        assert remote.name == "unit-test-dataset"
        assert remote.workspace.name == workspace.name
        assert remote.guidelines == "unit test guidelines"
        assert remote.allow_extra_metadata is False

        for remote_field, field in zip(remote.fields, feedback_dataset.fields):
            assert field.name == remote_field.name
            assert field.type == remote_field.type
            assert field.required == remote_field.required

        for remote_question, question in zip(remote.questions, feedback_dataset.questions):
            assert question.name == remote_question.name
            assert question.type == remote_question.type
            assert question.required == remote_question.required

        for remote_metadata_property, metadata_property in zip(
            remote.metadata_properties, feedback_dataset.metadata_properties
        ):
            assert metadata_property.name == remote_metadata_property.name
            assert metadata_property.type == remote_metadata_property.type

    @pytest.mark.parametrize(
        "metadata_property, RemoteMetadataPropertyCls",
        [
            (TermsMetadataProperty(name="new-terms-metadata"), RemoteTermsMetadataProperty),
            (TermsMetadataProperty(name="new-terms-metadata", values=["a", "b", "c"]), RemoteTermsMetadataProperty),
            (IntegerMetadataProperty(name="new-integer-metadata"), RemoteIntegerMetadataProperty),
            (IntegerMetadataProperty(name="new-integer-metadata", min=0, max=10), RemoteIntegerMetadataProperty),
            (FloatMetadataProperty(name="new-float-metadata"), RemoteFloatMetadataProperty),
            (FloatMetadataProperty(name="new-float-metadata", min=0.0, max=10.0), RemoteFloatMetadataProperty),
        ],
    )
    async def test_add_metadata_property(
        self,
        owner: "User",
        test_dataset: FeedbackDataset,
        metadata_property: "AllowedMetadataPropertyTypes",
        RemoteMetadataPropertyCls: Type["AllowedRemoteMetadataPropertyTypes"],
    ) -> None:
        api.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test-workspace")

        remote_dataset = test_dataset.push_to_argilla(name="test_dataset", workspace=workspace)
        remote_metadata_property = remote_dataset.add_metadata_property(metadata_property)

        assert isinstance(remote_metadata_property, RemoteMetadataPropertyCls)
        assert remote_metadata_property.name == metadata_property.name

        remote_dataset = FeedbackDataset.from_argilla(id=remote_dataset.id)
        remote_metadata_property = remote_dataset.metadata_property_by_name(remote_metadata_property.name)
        assert remote_metadata_property.to_local() == metadata_property

    async def test_delete_metadata_property(self, owner: "User", feedback_dataset: FeedbackDataset) -> None:
        api.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test-workspace")

        remote_dataset = feedback_dataset.push_to_argilla(name="test_dataset", workspace=workspace)
        assert isinstance(remote_dataset, RemoteFeedbackDataset)
        assert len(remote_dataset.metadata_properties) == len(feedback_dataset.metadata_properties)

        for idx, metadata_property in enumerate(remote_dataset.metadata_properties, 1):
            remote_dataset.delete_metadata_properties(metadata_property.name)
            assert len(remote_dataset.metadata_properties) == len(feedback_dataset.metadata_properties) - idx

        assert len(remote_dataset.metadata_properties) == 0

    async def test_delete_metadata_property_in_place(self, owner: "User", feedback_dataset: FeedbackDataset) -> None:
        api.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test-workspace")

        remote_dataset = feedback_dataset.push_to_argilla(name="test_dataset", workspace=workspace)
        assert isinstance(remote_dataset, RemoteFeedbackDataset)
        assert len(remote_dataset.metadata_properties) == len(feedback_dataset.metadata_properties)

        for idx, metadata_property in enumerate(remote_dataset.metadata_properties, 1):
            metadata_property.delete()
            assert len(remote_dataset.metadata_properties) == len(feedback_dataset.metadata_properties) - idx

        assert len(remote_dataset.metadata_properties) == 0

    @pytest.mark.parametrize(
        "metadata_properties, RemoteMetadataPropertiesClasses",
        [
            (
                [
                    TermsMetadataProperty(name="new-terms-metadata"),
                    IntegerMetadataProperty(name="new-integer-metadata"),
                    FloatMetadataProperty(name="new-float-metadata"),
                ],
                [
                    RemoteTermsMetadataProperty,
                    RemoteIntegerMetadataProperty,
                    RemoteFloatMetadataProperty,
                ],
            ),
            (
                [
                    TermsMetadataProperty(name="new-terms-metadata", values=["a", "b", "c"]),
                    IntegerMetadataProperty(name="new-integer-metadata", min=0, max=10),
                    FloatMetadataProperty(name="new-float-metadata", min=0.0, max=10.0),
                ],
                [
                    RemoteTermsMetadataProperty,
                    RemoteIntegerMetadataProperty,
                    RemoteFloatMetadataProperty,
                ],
            ),
        ],
    )
    async def test_add_metadata_property_sequential(
        self,
        owner: "User",
        test_dataset: FeedbackDataset,
        metadata_properties: List["AllowedMetadataPropertyTypes"],
        RemoteMetadataPropertiesClasses: List[Type["AllowedRemoteMetadataPropertyTypes"]],
    ) -> None:
        api.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test-workspace")

        dataset = test_dataset.push_to_argilla(name="test_dataset", workspace=workspace)

        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        assert len(remote_dataset.metadata_properties) == len(test_dataset.metadata_properties)

        for idx, (metadata_property, remote_metadata_property_cls) in enumerate(
            zip(metadata_properties, RemoteMetadataPropertiesClasses), start=len(test_dataset.metadata_properties)
        ):
            remote_metadata_property = remote_dataset.add_metadata_property(metadata_property)
            assert isinstance(remote_metadata_property, remote_metadata_property_cls)
            assert remote_metadata_property.name == metadata_property.name
            assert len(remote_dataset.metadata_properties) == (idx + 1)

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
    async def test_delete_records(self, owner: "User", test_dataset: FeedbackDataset, role: UserRole) -> None:
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
