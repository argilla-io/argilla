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

import argilla_v1.client.singleton
import pytest
from argilla_server.models import User
from argilla_v1 import SortBy, TextField, TextQuestion
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas.enums import ResponseStatusFilter
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataFilter,
    FloatMetadataProperty,
    IntegerMetadataFilter,
    IntegerMetadataProperty,
    MetadataFilters,
    TermsMetadataFilter,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
from argilla_v1.client.sdk.users.models import UserRole
from argilla_v1.client.workspaces import Workspace
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
)


@pytest.fixture()
def test_dataset():
    dataset = FeedbackDataset(
        fields=[TextField(name="text")],
        questions=[TextQuestion(name="question")],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="integer-metadata"),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    return dataset


@pytest.mark.asyncio
class TestFilteredRemoteFeedbackDataset:
    @pytest.mark.skip(reason="Avoid using factory tests")
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    @pytest.mark.parametrize(
        "statuses, expected_num_records",
        [
            ([ResponseStatusFilter.draft], 1),
            ([ResponseStatusFilter.pending], 10),
            ([ResponseStatusFilter.discarded], 1),
            ([ResponseStatusFilter.submitted], 1),
            ([ResponseStatusFilter.discarded, ResponseStatusFilter.submitted], 2),
        ],
    )
    async def test_filter_by_response_status(
        self, role: UserRole, statuses: List[ResponseStatusFilter], expected_num_records: int
    ) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=True)
        records = await RecordFactory.create_batch(dataset=dataset, size=10)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        for status, record in zip(statuses, records):
            if status != ResponseStatusFilter.pending:
                await ResponseFactory.create(record=record, status=status, values={})

        argilla_v1.client.singleton.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        filtered_dataset = remote_dataset.filter_by(response_status=statuses)
        assert all([isinstance(record, RemoteFeedbackRecord) for record in filtered_dataset.records])
        assert len(filtered_dataset.records) == expected_num_records

    @pytest.mark.parametrize(
        "metadata_filters, expected_num_records",
        [
            (TermsMetadataFilter(name="terms-metadata", values=["a"]), 100),
            (TermsMetadataFilter(name="terms-metadata", values=["a", "b"]), 100),
            (TermsMetadataFilter(name="terms-metadata", values=["a", "b", "c"]), 150),
            (IntegerMetadataFilter(name="integer-metadata", le=5), 100),
            (IntegerMetadataFilter(name="integer-metadata", ge=5), 50),
            (FloatMetadataFilter(name="float-metadata", ge=5.0), 50),
            (FloatMetadataFilter(name="float-metadata", le=5.0), 100),
        ],
    )
    def test_filter_by_metadata(
        self,
        owner: User,
        test_dataset: FeedbackDataset,
        metadata_filters: Union[MetadataFilters, List[MetadataFilters]],
        expected_num_records: int,
    ) -> None:
        argilla_v1.client.singleton.init(api_key=owner.api_key)

        ws = Workspace.create(name="test-workspace")

        remote_dataset = test_dataset.push_to_argilla(name="test-dataset", workspace=ws)
        for metadata in (
            {"terms-metadata": "a", "integer-metadata": 2, "float-metadata": 2.0},
            {"terms-metadata": "a", "integer-metadata": 4, "float-metadata": 4.0},
            {"terms-metadata": "c", "integer-metadata": 6, "float-metadata": 6.0},
        ):
            remote_dataset.add_records([FeedbackRecord(fields={"text": "text"}, metadata=metadata) for _ in range(50)])

        filtered_dataset = remote_dataset.filter_by(metadata_filters=metadata_filters)
        assert all([isinstance(record, RemoteFeedbackRecord) for record in filtered_dataset.records])
        assert len(filtered_dataset.records) == expected_num_records

    async def test_filter_by_response_status_without_results(
        self,
        argilla_user: User,
        feedback_dataset_guidelines: str,
        feedback_dataset_fields: List[AllowedFieldTypes],
        feedback_dataset_questions: List[AllowedQuestionTypes],
        feedback_dataset_records: List[FeedbackRecord],
        db: AsyncSession,
    ) -> None:
        argilla_v1.client.singleton.active_api()
        argilla_v1.client.singleton.init(api_key=argilla_user.api_key)

        dataset = FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )
        dataset.add_records(records=feedback_dataset_records)
        dataset.push_to_argilla(name="test-dataset")

        await db.refresh(argilla_user, attribute_names=["datasets"])
        same_dataset = FeedbackDataset.from_argilla(name="test-dataset")
        filtered_dataset = same_dataset.filter_by(response_status=ResponseStatusFilter.draft).pull()

        assert filtered_dataset is not None
        assert len(filtered_dataset.records) == 0

        filtered_dataset = same_dataset.filter_by(response_status=ResponseStatusFilter.submitted).pull(max_records=1)

        assert filtered_dataset is not None
        assert len(filtered_dataset.records) == 1

    def test_filter_by_overrides_previous_values(self, owner: "User", test_dataset: FeedbackDataset):
        remote = self._create_test_dataset_with_records(owner, test_dataset)

        filtered_dataset = (
            remote.filter_by(metadata_filters=IntegerMetadataFilter(name="integer-metadata", ge=4, le=5))
            .filter_by(metadata_filters=IntegerMetadataFilter(name="integer-metadata", ge=5))
            .filter_by(metadata_filters=IntegerMetadataFilter(name="integer-metadata", le=5))
        )

        records = list(filtered_dataset.records)

        another_filtered_dataset = remote.filter_by(
            metadata_filters=IntegerMetadataFilter(name="integer-metadata", le=5)
        )
        other_records = list(another_filtered_dataset.records)

        assert records == other_records

    @pytest.mark.skip(reason="Avoid using factory tests")
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

        argilla_v1.client.singleton.init(api_key=user.api_key)
        remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
        filtered_dataset = remote_dataset.filter_by(response_status="submitted")

        assert isinstance(filtered_dataset.id, UUID)
        assert isinstance(filtered_dataset.name, str)
        assert isinstance(filtered_dataset.workspace, Workspace)
        assert isinstance(filtered_dataset.url, str)
        assert isinstance(filtered_dataset.created_at, datetime)
        assert isinstance(filtered_dataset.updated_at, datetime)

    def test_basic_sorting(self, owner: "User", test_dataset: FeedbackDataset):
        remote = self._create_test_dataset_with_records(owner, test_dataset)

        expected_terms_values = ["a", "a", "a", "a", "b", "b", "b", "b", "c", "c"]

        assert [
            r.metadata["terms-metadata"]
            for r in remote.sort_by([SortBy(field="metadata.terms-metadata", order="asc")]).records
        ] == expected_terms_values

        assert [
            r.metadata["terms-metadata"]
            for r in remote.sort_by([SortBy(field="metadata.terms-metadata", order="desc")]).records
        ] == sorted(expected_terms_values, reverse=True)

    def test_sorting_with_filter(self, owner: "User", test_dataset: FeedbackDataset):
        remote = self._create_test_dataset_with_records(owner, test_dataset)

        sort_cfg = [SortBy(field="metadata.terms-metadata", order="desc")]
        metadata_filter = IntegerMetadataFilter(name="integer-metadata", ge=4, le=5)

        new_ds = remote.filter_by(metadata_filters=metadata_filter).sort_by(sort_cfg)
        assert [r.metadata["terms-metadata"] for r in new_ds.records] == ["b", "b", "b", "b", "a", "a"]

        new_ds = remote.sort_by(sort_cfg).filter_by(metadata_filters=metadata_filter)
        assert [r.metadata["terms-metadata"] for r in new_ds.records] == ["b", "b", "b", "b", "a", "a"]

    def test_sort_by_overrides_previous_values(self, owner: "User", test_dataset: FeedbackDataset):
        remote = self._create_test_dataset_with_records(owner, test_dataset)

        sorted_dataset = (
            remote.sort_by([SortBy(field="metadata.terms-metadata", order="desc")])
            .sort_by([SortBy(field="inserted_at", order="desc")])
            .sort_by([SortBy(field="metadata.terms-metadata", order="asc")])
        )

        records = list(sorted_dataset.records)

        another_sorted_dataset = remote.sort_by([SortBy(field="metadata.terms-metadata", order="asc")])
        other_records = list(another_sorted_dataset.records)

        assert records == other_records

    def test_sort_by_with_wrong_field(self, owner: "User", test_dataset: FeedbackDataset):
        remote = self._create_test_dataset_with_records(owner, test_dataset)

        with pytest.raises(
            ValueError,
            match="The metadata property name `unexpected-field` does not exist in the current `FeedbackDataset` "
            "in Argilla. ",
        ):
            remote.sort_by([SortBy(field="metadata.unexpected-field", order="desc")])

    def test_filter_by_wrong_field(self, owner: "User", test_dataset: FeedbackDataset):
        remote = self._create_test_dataset_with_records(owner, test_dataset)

        with pytest.raises(
            ValueError,
            match="The metadata property name `unexpected-field` does not exist in the current `FeedbackDataset` "
            "in Argilla. ",
        ):
            remote.filter_by(metadata_filters=IntegerMetadataFilter(name="unexpected-field", ge=4, le=5))

    def _create_test_dataset_with_records(self, owner: User, test_dataset: FeedbackDataset):
        argilla_v1.client.singleton.init(api_key=owner.api_key)
        ws = Workspace.create(name="test-workspace")
        remote = test_dataset.push_to_argilla(name="test_dataset", workspace=ws)
        for metadata in (
            {"terms-metadata": "a", "integer-metadata": 2, "float-metadata": 2.0},
            {"terms-metadata": "a", "integer-metadata": 4, "float-metadata": 4.0},
            {"terms-metadata": "b", "integer-metadata": 4, "float-metadata": 4.0},
            {"terms-metadata": "b", "integer-metadata": 5, "float-metadata": 4.0},
            {"terms-metadata": "c", "integer-metadata": 6, "float-metadata": 6.0},
        ):
            remote.add_records([FeedbackRecord(fields={"text": "text"}, metadata=metadata) for _ in range(2)])
        return remote
