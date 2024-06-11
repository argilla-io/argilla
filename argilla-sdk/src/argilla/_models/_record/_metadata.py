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

from typing import Annotated, Union, List

from pydantic import BaseModel


MetadataValue = Annotated[Union[str, List[str], float, int, None], "The value of the metadata field dictionary"]


class MetadataModel(BaseModel):
    """Schema for the metadata of a `Dataset`"""

    name: Annotated[str, "The name of the metadata field or key in the metadata dictionary"]
    value: MetadataValue
