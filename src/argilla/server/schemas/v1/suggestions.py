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

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel

from argilla.server.models import SuggestionType


class BaseSuggestion(BaseModel):
    question_id: UUID
    type: Optional[SuggestionType]
    score: Optional[float]
    value: Any
    agent: Optional[str]


class SuggestionCreate(BaseSuggestion):
    pass


class Suggestion(BaseSuggestion):
    id: UUID

    class Config:
        orm_mode = True


class Suggestions(BaseModel):
    items: List[Suggestion]
