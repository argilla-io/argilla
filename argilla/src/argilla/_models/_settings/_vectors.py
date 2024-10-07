# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
from uuid import UUID

from pydantic import field_validator, field_serializer
from pydantic_core.core_schema import ValidationInfo

from argilla._models import ResourceModel
from argilla._helpers import log_message


class VectorFieldModel(ResourceModel):
    name: str
    title: Optional[str] = None
    dimensions: int
    dataset_id: Optional[UUID] = None

    @field_serializer("id", "dataset_id", when_used="unless-none")
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    @field_validator("title")
    @classmethod
    def _title_default(cls, title: str, info: ValidationInfo) -> str:
        data = info.data
        validated_title = title or data["name"]
        log_message(f"TextField title is {validated_title}")
        return validated_title

    @field_validator("dimensions")
    @classmethod
    def _dimension_gt_zero(cls, dimensions):
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than 0")
        return dimensions
