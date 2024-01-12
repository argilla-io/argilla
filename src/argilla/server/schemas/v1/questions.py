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
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from typing_extensions import Annotated

from argilla.server.models import QuestionType
from argilla.server.pydantic_v1 import BaseModel, Field, PositiveInt, conlist, constr, root_validator, validator
from argilla.server.schemas.base import UpdateSchema

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


QUESTION_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"
QUESTION_CREATE_NAME_MIN_LENGTH = 1
QUESTION_CREATE_NAME_MAX_LENGTH = 200

QUESTION_CREATE_TITLE_MIN_LENGTH = 1
QUESTION_CREATE_TITLE_MAX_LENGTH = 500

QUESTION_CREATE_DESCRIPTION_MIN_LENGTH = 1
QUESTION_CREATE_DESCRIPTION_MAX_LENGTH = 1000

VALUE_TEXT_OPTION_VALUE_MIN_LENGTH = 1
VALUE_TEXT_OPTION_VALUE_MAX_LENGTH = 200
VALUE_TEXT_OPTION_TEXT_MIN_LENGTH = 1
VALUE_TEXT_OPTION_TEXT_MAX_LENGTH = 500
VALUE_TEXT_OPTION_DESCRIPTION_MIN_LENGTH = 1
VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH = 1000

LABEL_SELECTION_OPTIONS_MIN_ITEMS = 2
LABEL_SELECTION_OPTIONS_MAX_ITEMS = 250
LABEL_SELECTION_MIN_VISIBLE_OPTIONS = 3

RANKING_OPTIONS_MIN_ITEMS = 2
RANKING_OPTIONS_MAX_ITEMS = 50

RATING_OPTIONS_MIN_ITEMS = 2
RATING_OPTIONS_MAX_ITEMS = 10
RATING_LOWER_VALUE_ALLOWED = 1
RATING_UPPER_VALUE_ALLOWED = 10


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
    visible_options: Optional[int] = None


class MultiLabelSelectionQuestionSettings(LabelSelectionQuestionSettings):
    type: Literal[QuestionType.multi_label_selection]


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


class TextQuestionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.text]
    use_markdown: Optional[bool]

    __non_nullable_fields__ = {"use_markdown"}


class RatingQuestionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.rating]


class LabelSelectionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.label_selection]
    visible_options: Optional[PositiveInt]


class MultiLabelSelectionQuestionSettingsUpdate(LabelSelectionSettingsUpdate):
    type: Literal[QuestionType.multi_label_selection]


class RankingQuestionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.ranking]


QuestionSettingsUpdate = Annotated[
    Union[
        TextQuestionSettingsUpdate,
        RatingQuestionSettingsUpdate,
        LabelSelectionSettingsUpdate,
        MultiLabelSelectionQuestionSettingsUpdate,
        RankingQuestionSettingsUpdate,
    ],
    Field(..., discriminator="type"),
]


QuestionName = Annotated[
    constr(
        regex=QUESTION_CREATE_NAME_REGEX,
        min_length=QUESTION_CREATE_NAME_MIN_LENGTH,
        max_length=QUESTION_CREATE_NAME_MAX_LENGTH,
    ),
    Field(..., description="The name of the question"),
]


QuestionTitle = Annotated[
    constr(
        min_length=QUESTION_CREATE_TITLE_MIN_LENGTH,
        max_length=QUESTION_CREATE_TITLE_MAX_LENGTH,
    ),
    Field(..., description="The title of the question"),
]


QuestionDescription = Annotated[
    constr(
        min_length=QUESTION_CREATE_DESCRIPTION_MIN_LENGTH,
        max_length=QUESTION_CREATE_DESCRIPTION_MAX_LENGTH,
    ),
    Field(..., description="The description of the question"),
]


class UniqueValuesCheckerMixin(BaseModel):
    @root_validator(skip_on_failure=True)
    def check_unique_values(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        options = values.get("options", [])
        seen = set()
        duplicates = set()
        for option in options:
            if option.value in seen:
                duplicates.add(option.value)
            else:
                seen.add(option.value)
        if duplicates:
            raise ValueError(f"Option values must be unique, found duplicates: {duplicates}")
        return values


class TextQuestionSettingsCreate(BaseModel):
    type: Literal[QuestionType.text]
    use_markdown: bool = False


class RatingQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.rating]
    options: conlist(
        item_type=RatingQuestionSettingsOption,
        min_items=RATING_OPTIONS_MIN_ITEMS,
        max_items=RATING_OPTIONS_MAX_ITEMS,
    )

    @validator("options")
    def check_option_value_range(cls, options: List[RatingQuestionSettingsOption]):
        """Validator to control all values are in allowed range 1 <= x <= 10"""
        for option in options:
            if not RATING_LOWER_VALUE_ALLOWED <= option.value <= RATING_UPPER_VALUE_ALLOWED:
                raise ValueError(
                    f"Option value {option.value!r} out of range "
                    f"[{RATING_LOWER_VALUE_ALLOWED!r}, {RATING_UPPER_VALUE_ALLOWED!r}]"
                )
        return options


class ValueTextQuestionSettingsOptionCreate(BaseModel):
    value: constr(
        min_length=VALUE_TEXT_OPTION_VALUE_MIN_LENGTH,
        max_length=VALUE_TEXT_OPTION_VALUE_MAX_LENGTH,
    )
    text: constr(
        min_length=VALUE_TEXT_OPTION_TEXT_MIN_LENGTH,
        max_length=VALUE_TEXT_OPTION_TEXT_MAX_LENGTH,
    )
    description: Optional[
        constr(
            min_length=VALUE_TEXT_OPTION_DESCRIPTION_MIN_LENGTH,
            max_length=VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH,
        )
    ] = None


class LabelSelectionQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.label_selection]
    options: conlist(
        item_type=ValueTextQuestionSettingsOptionCreate,
        min_items=LABEL_SELECTION_OPTIONS_MIN_ITEMS,
        max_items=LABEL_SELECTION_OPTIONS_MAX_ITEMS,
    )
    visible_options: Optional[int] = Field(None, ge=LABEL_SELECTION_MIN_VISIBLE_OPTIONS)

    @root_validator(skip_on_failure=True)
    def check_visible_options_value(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        visible_options = values.get("visible_options")
        if visible_options is not None:
            num_options = len(values["options"])
            if visible_options > num_options:
                raise ValueError(
                    "The value for 'visible_options' must be less or equal to the number of items in 'options'"
                    f" ({num_options})"
                )
        return values


class MultiLabelSelectionQuestionSettingsCreate(LabelSelectionQuestionSettingsCreate):
    type: Literal[QuestionType.multi_label_selection]


class RankingQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.ranking]
    options: conlist(
        item_type=ValueTextQuestionSettingsOptionCreate,
        min_items=RANKING_OPTIONS_MIN_ITEMS,
        max_items=RANKING_OPTIONS_MAX_ITEMS,
    )


QuestionSettingsCreate = Annotated[
    Union[
        TextQuestionSettingsCreate,
        RatingQuestionSettingsCreate,
        LabelSelectionQuestionSettingsCreate,
        MultiLabelSelectionQuestionSettingsCreate,
        RankingQuestionSettingsCreate,
    ],
    Field(discriminator="type"),
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


class Questions(BaseModel):
    items: List[Question]


class QuestionCreate(BaseModel):
    name: QuestionName
    title: QuestionTitle
    description: Optional[QuestionDescription]
    required: Optional[bool]
    settings: QuestionSettingsCreate


class QuestionUpdate(UpdateSchema):
    title: Optional[QuestionTitle]
    description: Optional[QuestionDescription]
    settings: Optional[QuestionSettingsUpdate]

    __non_nullable_fields__ = {"title", "settings"}
