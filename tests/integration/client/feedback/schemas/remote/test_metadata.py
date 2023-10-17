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

from typing import TYPE_CHECKING, List, Type, Union

import argilla as rg
import pytest
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedMetadataPropertyTypes
    from argilla.client.sdk.users.models import UserModel


class TestSuiteRemoteMetadataProperties:
    @pytest.mark.parametrize(
        "metadata_properties",
        (
            [rg.TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
            [rg.TermsMetadataProperty(name="terms-metadata", visible_for_annotators=False)],
            [rg.IntegerMetadataProperty(name="integer-metadata", min=0, max=10)],
            [rg.IntegerMetadataProperty(name="integer-metadata", visible_for_annotators=False)],
            [rg.FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            [rg.FloatMetadataProperty(name="float-metadata", visible_for_annotators=False)],
            [
                rg.TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
                rg.IntegerMetadataProperty(name="integer-metadata", min=0, max=10),
                rg.FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
            ],
        ),
    )
    def test_create_and_restore(
        self, owner: "UserModel", metadata_properties: List["AllowedMetadataPropertyTypes"]
    ) -> None:
        rg.init(api_key=owner.api_key)

        workspace = rg.Workspace.create(name="my-workspace")
        dataset = rg.FeedbackDataset(
            fields=[rg.TextField(name="text-field")],
            questions=[rg.TextQuestion(name="text-question")],
            metadata_properties=metadata_properties,
        )

        remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace=workspace.name)
        assert isinstance(remote_dataset, RemoteFeedbackDataset)
        assert len(remote_dataset.metadata_properties) == len(dataset.metadata_properties)

        for remote_metadata_property in remote_dataset.metadata_properties:
            assert isinstance(
                remote_metadata_property,
                (RemoteTermsMetadataProperty, RemoteIntegerMetadataProperty, RemoteFloatMetadataProperty),
            )
            matching_metadata_property = next(
                metadata_property
                for metadata_property in dataset.metadata_properties
                if metadata_property.name == remote_metadata_property.name
            )
            assert isinstance(
                matching_metadata_property,
                (rg.TermsMetadataProperty, rg.IntegerMetadataProperty, rg.FloatMetadataProperty),
            )
            assert remote_metadata_property.to_local() == matching_metadata_property

    @pytest.mark.parametrize(
        "metadata_properties, title, visible_for_annotators",
        [
            (
                [rg.TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
                "new-title",
                False,
            ),
            (
                [rg.IntegerMetadataProperty(name="integer-metadata", min=0, max=10)],
                "new-title",
                False,
            ),
            (
                [rg.FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
                "new-title",
                False,
            ),
            (
                [
                    rg.TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
                    rg.IntegerMetadataProperty(name="integer-metadata", min=0, max=10),
                    rg.FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
                ],
                "new-title",
                False,
            ),
        ],
    )
    def test_update(
        self,
        owner: "UserModel",
        metadata_properties: List["AllowedMetadataPropertyTypes"],
        title: str,
        visible_for_annotators: bool,
    ) -> None:
        rg.init(api_key=owner.api_key)

        workspace = rg.Workspace.create(name="my-workspace")
        dataset = rg.FeedbackDataset(
            fields=[rg.TextField(name="text-field")],
            questions=[rg.TextQuestion(name="text-question")],
            metadata_properties=metadata_properties,
        )

        remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace=workspace.name)
        assert isinstance(remote_dataset, RemoteFeedbackDataset)
        assert len(remote_dataset.metadata_properties) == len(dataset.metadata_properties)

        # Ensure that the in-place `update` for `metadata_properties` works as expected
        for metadata_property in remote_dataset.metadata_properties:
            metadata_property.title = title
            metadata_property.visible_for_annotators = visible_for_annotators
            metadata_property.update()

        # Ensure that `metadata_properties` are updated in Argilla and restored successfully
        remote_dataset = rg.FeedbackDataset.from_argilla(name="my-dataset", workspace=workspace.name)
        assert isinstance(remote_dataset, RemoteFeedbackDataset)
        assert len(remote_dataset.metadata_properties) == len(dataset.metadata_properties)

        for metadata_property in remote_dataset.metadata_properties:
            assert metadata_property.title == title
            assert metadata_property.visible_for_annotators == visible_for_annotators

    def test_delete(self, owner: "UserModel") -> None:
        rg.init(api_key=owner.api_key)

        workspace = rg.Workspace.create(name="my-workspace")
        dataset = rg.FeedbackDataset(
            fields=[rg.TextField(name="text-field")],
            questions=[rg.TextQuestion(name="text-question")],
            metadata_properties=[
                rg.TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
                rg.IntegerMetadataProperty(name="integer-metadata", min=0, max=10),
                rg.FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
            ],
        )

        remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace=workspace.name)
        assert isinstance(remote_dataset, RemoteFeedbackDataset)
        assert len(remote_dataset.metadata_properties) == len(dataset.metadata_properties)

        remote_dataset.metadata_properties[0].delete()
        for metadata_property in remote_dataset.metadata_properties:
            local_metadata_property = metadata_property.delete()
            assert isinstance(
                local_metadata_property,
                (rg.TermsMetadataProperty, rg.IntegerMetadataProperty, rg.FloatMetadataProperty),
            )
        assert len(remote_dataset.metadata_properties) == 0
