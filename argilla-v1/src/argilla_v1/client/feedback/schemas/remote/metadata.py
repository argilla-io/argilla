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

from typing import TYPE_CHECKING, Dict, Optional, Type, Union

from argilla_v1.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.remote.shared import RemoteSchema

if TYPE_CHECKING:
    import httpx

    from argilla_v1.client.sdk.v1.datasets.models import FeedbackMetadataPropertyModel


class RemoteTermsMetadataProperty(TermsMetadataProperty, RemoteSchema):
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


class RemoteIntegerMetadataProperty(IntegerMetadataProperty, RemoteSchema):
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


class RemoteFloatMetadataProperty(FloatMetadataProperty, RemoteSchema):
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
    Type[Union[RemoteTermsMetadataProperty, RemoteIntegerMetadataProperty, RemoteFloatMetadataProperty]],
] = {
    MetadataPropertyTypes.terms: RemoteTermsMetadataProperty,
    MetadataPropertyTypes.integer: RemoteIntegerMetadataProperty,
    MetadataPropertyTypes.float: RemoteFloatMetadataProperty,
}
