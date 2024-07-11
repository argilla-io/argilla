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
import re
from typing import List

from pydantic import field_validator

from argilla._models import ResourceModel

__all__ = ["VectorModel", "VectorValue"]

VectorValue = List[float]


class VectorModel(ResourceModel):
    name: str
    vector_values: VectorValue

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """Validate the name of the vector is url safe"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValueError("Vector name must be url safe")
        return value
