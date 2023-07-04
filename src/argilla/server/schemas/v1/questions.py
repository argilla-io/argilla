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

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from argilla.server.models import QuestionType


class TextQuestionSettings(BaseModel):
    type: Literal[QuestionType.text]
    use_markdown: bool = False


class RatingQuestionSettingsOption(BaseModel):
    value: int


class RatingQuestionSettings(BaseModel):
    type: Literal[QuestionType.rating]
    options: conlist(item_type=RatingQuestionSettingsOption)


class ValueTextQuestionSettingsOption(BaseModel):
    value: str
    text: str
    description: Optional[str] = None


class LabelSelectionQuestionSettings(BaseModel):
    type: Literal[QuestionType.label_selection]
    options: conlist(item_type=ValueTextQuestionSettingsOption)


class MultiLabelSelectionQuestionSettings(BaseModel):
    type: Literal[QuestionType.multi_label_selection]
    options: conlist(item_type=ValueTextQuestionSettingsOption)


class RankingQuestionSettings(BaseModel):
    type: Literal[QuestionType.ranking]
    options: conlist(item_type=ValueTextQuestionSettingsOption)


QuestionSettings = Annotated[
    Union[
        TextQuestionSettings,
        RatingQuestionSettings,
        LabelSelectionQuestionSettings,
        MultiLabelSelectionQuestionSettings,
        RankingQuestionSettings,
    ],
    Field(..., discriminator="type"),
]


class Question(BaseModel):
    id: UUID
    name: str
    title: str
    description: Optional[str]
    required: bool
    settings: QuestionSettings
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
