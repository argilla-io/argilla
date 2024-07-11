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

from argilla._models import ResourceModel

import re
from pydantic import field_validator, ConfigDict

__all__ = ["WorkspaceModel"]


class WorkspaceModel(ResourceModel):
    name: str

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """Validate the name of the workspace is url safe"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValueError("Workspace name must be url safe")
        return value
