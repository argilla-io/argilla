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
from uuid import UUID

from argilla.client.feedback.schemas.vector_settings import VectorSettings
from argilla.client.sdk.v1.datasets.models import FeedbackVectorSettingsModel


class RemoteVectorSettings(VectorSettings):
    id: UUID
    inserted_at: datetime
    updated_at: datetime

    def to_local(self) -> VectorSettings:
        return VectorSettings(name=self.name, title=self.title, dimensions=self.dimensions)

    @classmethod
    def from_api(cls, api_model: FeedbackVectorSettingsModel) -> "RemoteVectorSettings":
        return RemoteVectorSettings(
            id=api_model.id,
            name=api_model.name,
            title=api_model.title,
            dimensions=api_model.dimensions,
            inserted_at=api_model.inserted_at,
            updated_at=api_model.updated_at,
        )
