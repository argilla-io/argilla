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

from typing import TYPE_CHECKING, Dict, Optional, Union

from argilla.client.feedback.mixins import ArgillaMetadataPropertiesMixin
from argilla.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.remote.shared import RemoteSchema
from argilla.client.sdk.users.models import UserRole
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    import httpx

    from argilla.client.feedback.schemas.types import AllowedMetadataPropertyTypes, AllowedRemoteMetadataPropertyTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackMetadataPropertyModel


class _RemoteMetadataProperty(RemoteSchema):
    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def update(
        self: "AllowedRemoteMetadataPropertyTypes",
        title: Optional[str] = None,
        visible_for_annotators: Optional[bool] = None,
    ) -> None:
        """Updates the `RemoteMetadataProperty` in Argilla.

        Args:
            title: the new title of the metadata property. Defaults to `None`.
            visible_for_annotators: whether the metadata property should be visible for annotators. Defaults to `None`.

        Returns:
            The updated `RemoteMetadataProperty` object.
        """
        if title is None and visible_for_annotators is None:
            raise ValueError("At least one of `title` or `visible_for_annotators` must be provided and not `None`.")
        if title is not None and title == self.title:
            raise ValueError(
                f"Provided `title={title}` is the same as the current one `{self.title}`, you need either to provide"
                " a different one, or just pass it empty."
            )
        if visible_for_annotators is not None and visible_for_annotators == self.visible_for_annotators:
            raise ValueError(
                f"Provided `visible_for_annotators={visible_for_annotators}` is the same as the current one"
                f" `{self.visible_for_annotators}`, you need either to provide a different one, or just pass it empty."
            )
        updated_metadata_property = ArgillaMetadataPropertiesMixin.update(
            client=self.client,
            metadata_property_id=self.id,
            title=title,
            visible_for_annotators=visible_for_annotators,
        )
        self.__dict__.update(updated_metadata_property.__dict__)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self: "AllowedRemoteMetadataPropertyTypes") -> "AllowedMetadataPropertyTypes":
        """Deletes the `RemoteMetadataProperty` from Argilla.

        Returns:
            The deleted `RemoteMetadataProperty` as a `MetadataProperty` object.
        """
        return ArgillaMetadataPropertiesMixin.delete(client=self.client, metadata_property_id=self.id)


class RemoteTermsMetadataProperty(TermsMetadataProperty, _RemoteMetadataProperty):
    def to_local(self) -> TermsMetadataProperty:
        return TermsMetadataProperty(
            name=self.name,
            title=self.title,
            visible_for_annotators=self.visible_for_annotators,
            values=self.values,
        )

    @classmethod
    def from_api(
        cls, payload: "FeedbackMetadataPropertyModel", client: Optional["httpx.Client"] = None
    ) -> "RemoteTermsMetadataProperty":
        return RemoteTermsMetadataProperty(
            client=client,
            id=payload.id,
            name=payload.name,
            title=payload.title,
            visible_for_annotators=payload.visible_for_annotators,
            values=payload.settings.get("values", None),
        )


class RemoteIntegerMetadataProperty(IntegerMetadataProperty, _RemoteMetadataProperty):
    def to_local(self) -> IntegerMetadataProperty:
        return IntegerMetadataProperty(
            name=self.name,
            title=self.title,
            visible_for_annotators=self.visible_for_annotators,
            min=self.min,
            max=self.max,
        )

    @classmethod
    def from_api(
        cls, payload: "FeedbackMetadataPropertyModel", client: Optional["httpx.Client"] = None
    ) -> "RemoteIntegerMetadataProperty":
        return RemoteIntegerMetadataProperty(
            client=client,
            id=payload.id,
            name=payload.name,
            title=payload.title,
            visible_for_annotators=payload.visible_for_annotators,
            min=payload.settings.get("min", None),
            max=payload.settings.get("max", None),
        )


class RemoteFloatMetadataProperty(FloatMetadataProperty, _RemoteMetadataProperty):
    def to_local(self) -> FloatMetadataProperty:
        return FloatMetadataProperty(
            name=self.name,
            title=self.title,
            visible_for_annotators=self.visible_for_annotators,
            min=self.min,
            max=self.max,
        )

    @classmethod
    def from_api(
        cls, payload: "FeedbackMetadataPropertyModel", client: Optional["httpx.Client"] = None
    ) -> "RemoteFloatMetadataProperty":
        return RemoteFloatMetadataProperty(
            client=client,
            id=payload.id,
            name=payload.name,
            title=payload.title,
            visible_for_annotators=payload.visible_for_annotators,
            min=payload.settings.get("min", None),
            max=payload.settings.get("max", None),
        )


RemoteMetadataPropertiesMapping: Dict[
    MetadataPropertyTypes,
    Union[RemoteTermsMetadataProperty, RemoteIntegerMetadataProperty, RemoteFloatMetadataProperty],
] = {
    MetadataPropertyTypes.terms: RemoteTermsMetadataProperty,
    MetadataPropertyTypes.integer: RemoteIntegerMetadataProperty,
    MetadataPropertyTypes.float: RemoteFloatMetadataProperty,
}
