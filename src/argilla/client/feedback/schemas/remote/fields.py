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

from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.remote.shared import RemoteSchema

if TYPE_CHECKING:
    from argilla.client.sdk.v1.datasets.models import FeedbackFieldModel


class RemoteTextField(TextField, RemoteSchema):
    def to_local(self) -> TextField:
        return TextField(
            name=self.name,
            title=self.title,
            required=self.required,
            use_markdown=self.use_markdown,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackFieldModel") -> "RemoteTextField":
        return RemoteTextField(
            id=payload.id,
            name=payload.name,
            title=payload.title,
            required=payload.required,
            use_markdown=payload.settings["use_markdown"],
        )
