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
from typing import Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, conlist

from argilla.server.models import QuestionType


class TextQuestionSettings(BaseModel):
    type: Literal[QuestionType.text]
    use_markdown: bool = False


class RatingQuestionSettingsOption(BaseModel):
    value: int


class RatingQuestionSettings(BaseModel):
    type: Literal[QuestionType.rating]
    options: conlist(item_type=RatingQuestionSettingsOption)


class Question(BaseModel):
    id: UUID
    name: str
    title: str
    description: Optional[str]
    required: bool
    settings: Union[TextQuestionSettings, RatingQuestionSettings] = Field(..., discriminator="type")
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
