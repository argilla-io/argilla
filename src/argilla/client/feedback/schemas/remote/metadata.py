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

from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.remote.shared import RemoteSchema

if TYPE_CHECKING:
    from argilla.client.sdk.v1.datasets.models import FeedbackMetadataPropertyModel


class RemoteTermsMetadataProperty(TermsMetadataProperty, RemoteSchema):
    def to_local(self) -> TermsMetadataProperty:
        return TermsMetadataProperty(
            name=self.name,
            description=self.description,
            # TODO: uncomment once API is ready
            # visible_for_annotators=self.visible_for_annotators,
            values=self.values,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackMetadataPropertyModel") -> "RemoteTermsMetadataProperty":
        return RemoteTermsMetadataProperty(
            name=payload.name,
            description=payload.description,
            # TODO: uncomment once API is ready
            # visible_for_annotators=payload.visible_for_annotators,
            values=payload.settings.get("values", None),
        )


class RemoteIntegerMetadataProperty(IntegerMetadataProperty, RemoteSchema):
    def to_local(self) -> IntegerMetadataProperty:
        return IntegerMetadataProperty(
            name=self.name,
            description=self.description,
            # TODO: uncomment once API is ready
            # visible_for_annotators=self.visible_for_annotators,
            min=self.min,
            max=self.max,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackMetadataPropertyModel") -> "RemoteIntegerMetadataProperty":
        return RemoteIntegerMetadataProperty(
            name=payload.name,
            description=payload.description,
            # TODO: uncomment once API is ready
            # visible_for_annotators=payload.visible_for_annotators,
            min=payload.settings.get("min", None),
            max=payload.settings.get("max", None),
        )


class RemoteFloatMetadataProperty(FloatMetadataProperty, RemoteSchema):
    def to_local(self) -> FloatMetadataProperty:
        return FloatMetadataProperty(
            name=self.name,
            description=self.description,
            # TODO: uncomment once API is ready
            # visible_for_annotators=self.visible_for_annotators,
            min=self.min,
            max=self.max,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackMetadataPropertyModel") -> "RemoteFloatMetadataProperty":
        return RemoteFloatMetadataProperty(
            name=payload.name,
            description=payload.description,
            # TODO: uncomment once API is ready
            # visible_for_annotators=payload.visible_for_annotators,
            min=payload.settings.get("min", None),
            max=payload.settings.get("max", None),
        )
