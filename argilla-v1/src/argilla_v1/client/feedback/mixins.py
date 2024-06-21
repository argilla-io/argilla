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

from typing import TYPE_CHECKING, List, Optional, Union

from argilla_v1.client.sdk.v1.datasets import api as datasets_api_v1
from argilla_v1.client.sdk.v1.datasets.models import FeedbackMetadataPropertyModel
from argilla_v1.client.sdk.v1.metadata_properties import api as metadata_properties_api_v1

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla_v1.client.feedback.schemas.types import (
        AllowedMetadataPropertyTypes,
        AllowedRemoteMetadataPropertyTypes,
    )


class ArgillaMetadataPropertiesMixin:
    @staticmethod
    def parse_payload(
        client: "httpx.Client", payload: Union[FeedbackMetadataPropertyModel, List[FeedbackMetadataPropertyModel]]
    ) -> List["AllowedRemoteMetadataPropertyTypes"]:
        from argilla_v1.client.feedback.schemas.remote.metadata import RemoteMetadataPropertiesMapping

        if isinstance(payload, FeedbackMetadataPropertyModel):
            payload = [payload]

        metadata_properties = list()
        for metadata_property in payload:
            metadata_properties.append(
                RemoteMetadataPropertiesMapping[metadata_property.settings["type"]].from_api(
                    payload=metadata_property,
                    client=client,
                )
            )
        return metadata_properties

    @staticmethod
    def list(client: "httpx.Client", dataset_id: "UUID") -> List["AllowedRemoteMetadataPropertyTypes"]:
        """Returns the list of metadata properties allowed for the given dataset, if any.

        Args:
            client: contains the `httpx.Client` instance that will be used to send requests to Argilla.
            dataset_id: contains the UUID of the dataset in Argilla.

        Returns:
            A list with the allowed metadata properties for the given dataset, if any.
        """
        response = datasets_api_v1.get_metadata_properties(client=client, id=dataset_id)
        if response.status_code == 200:
            return ArgillaMetadataPropertiesMixin.parse_payload(client=client, payload=response.parsed)

    @staticmethod
    def delete(client: "httpx.Client", metadata_property_id: "UUID") -> "AllowedMetadataPropertyTypes":
        """Deletes the metadata property with the given ID from Argilla.

        Args:
            client: contains the `httpx.Client` instance that will be used to send requests to Argilla.
            metadata_property_id: contains the UUID of the metadata property in Argilla.

        Returns:
            The deleted `RemoteMetadataProperty` as a `MetadataProperty` object.
        """
        response = metadata_properties_api_v1.delete_metadata_property(client=client, id=metadata_property_id)
        if response.status_code == 200:
            return ArgillaMetadataPropertiesMixin.parse_payload(client=client, payload=response.parsed)[0].to_local()

    @staticmethod
    def update(
        client: "httpx.Client",
        metadata_property_id: "UUID",
        title: Optional[str] = None,
        visible_for_annotators: Optional[bool] = None,
    ) -> "AllowedRemoteMetadataPropertyTypes":
        """Updates the metadata property with the given ID in Argilla.

        Args:
            client: contains the `httpx.Client` instance that will be used to send requests to Argilla.
            metadata_property_id: contains the UUID of the metadata property in Argilla.
            title: the new title of the metadata property. Defaults to `None`.
            visible_for_annotators: whether the metadata property should be visible for annotators. Defaults to `None`.

        Returns:
            The updated `RemoteMetadataProperty` object.
        """
        response = metadata_properties_api_v1.update_metadata_property(
            client=client,
            id=metadata_property_id,
            title=title,
            visible_for_annotators=visible_for_annotators,
        )
        if response.status_code == 200:
            return ArgillaMetadataPropertiesMixin.parse_payload(client=client, payload=response.parsed)[0]
