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

from typing import TYPE_CHECKING, List

import argilla_v1 as rg
import argilla_v1.client.singleton
import pytest
from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla_v1.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import AllowedMetadataPropertyTypes
    from argilla_v1.client.sdk.users.models import UserModel


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
        argilla_v1.client.singleton.init(api_key=owner.api_key)

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
