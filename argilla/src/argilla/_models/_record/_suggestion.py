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

from typing import Any, Optional, Literal, Union, List
from uuid import UUID, uuid4

from pydantic import BaseModel, field_serializer


class SuggestionModel(BaseModel):
    """Schema for the suggestions for the questions related to the record."""

    value: Any

    question_name: Optional[str] = None
    type: Optional[Literal["model", "human"]] = None
    score: Union[float, List[float], None] = None
    agent: Optional[str] = None
    id: Optional[UUID] = uuid4()
    question_id: Optional[UUID] = None

    @field_serializer("id", when_used="unless-none")
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    @field_serializer("question_id", when_used="unless-none")
    def serialize_question_id(self, value: UUID) -> str:
        return str(value)
