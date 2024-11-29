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
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from argilla_server.api.schemas.v1.commons import UpdateSchema
from argilla_server.api.schemas.v1.fields import FieldName
from argilla_server.enums import OptionsOrder, QuestionType
from pydantic import BaseModel, Field, conlist, constr, root_validator, ConfigDict, model_validator
from argilla_server.settings import settings

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

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
LABEL_SELECTION_MIN_VISIBLE_OPTIONS = 3

RANKING_OPTIONS_MIN_ITEMS = 2
RANKING_OPTIONS_MAX_ITEMS = 50

RATING_OPTIONS_MIN_ITEMS = 2
RATING_OPTIONS_MAX_ITEMS = 11
RATING_VALUE_GREATER_THAN_OR_EQUAL = 0
RATING_VALUE_LESS_THAN_OR_EQUAL = 10

SPAN_OPTIONS_MIN_ITEMS = 1
SPAN_MIN_VISIBLE_OPTIONS = 3


class UniqueValuesCheckerMixin(BaseModel):
    @model_validator(mode="after")
    @classmethod
    def check_unique_values(cls, instance: "UniqueValuesCheckerMixin") -> "UniqueValuesCheckerMixin":
        options = instance.options or []
        seen = set()
        duplicates = set()
        for option in options:
            if option.value in seen:
                duplicates.add(option.value)
            else:
                seen.add(option.value)
        if duplicates:
            raise ValueError(f"Option values must be unique, found duplicates: {duplicates}")
        return instance


# Option-based settings
class OptionSettings(BaseModel):
    value: str
    text: str
    description: Optional[str] = None


class OptionSettingsCreate(BaseModel):
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


# Text question
class TextQuestionSettings(BaseModel):
    type: Literal[QuestionType.text]
    use_markdown: bool = False


class TextQuestionSettingsCreate(BaseModel):
    type: Literal[QuestionType.text]
    use_markdown: bool = False


class TextQuestionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.text]
    use_markdown: Optional[bool] = None

    __non_nullable_fields__ = {"use_markdown"}


# Rating question
class RatingQuestionSettingsOption(BaseModel):
    value: int


class RatingQuestionSettingsOptionCreate(BaseModel):
    value: int = Field(ge=RATING_VALUE_GREATER_THAN_OR_EQUAL, le=RATING_VALUE_LESS_THAN_OR_EQUAL)


class RatingQuestionSettings(BaseModel):
    type: Literal[QuestionType.rating]
    options: List[RatingQuestionSettingsOption]


class RatingQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.rating]
    options: List[RatingQuestionSettingsOptionCreate] = Field(
        min_length=RATING_OPTIONS_MIN_ITEMS,
        max_length=RATING_OPTIONS_MAX_ITEMS,
    )


class RatingQuestionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.rating]


# Label selection question
class LabelSelectionQuestionSettings(BaseModel):
    type: Literal[QuestionType.label_selection]
    options: List[OptionSettings]
    visible_options: Optional[int] = None


class LabelSelectionQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.label_selection]
    options: conlist(
        item_type=OptionSettingsCreate,
        min_length=LABEL_SELECTION_OPTIONS_MIN_ITEMS,
        max_length=settings.label_selection_options_max_items,
    )
    visible_options: Optional[int] = Field(None, ge=LABEL_SELECTION_MIN_VISIBLE_OPTIONS)

    @model_validator(mode="after")
    @classmethod
    def check_visible_options_value(
        cls, instance: "LabelSelectionQuestionSettingsCreate"
    ) -> "LabelSelectionQuestionSettingsCreate":
        visible_options = instance.visible_options
        if visible_options is not None:
            num_options = len(instance.options)
            if visible_options > num_options:
                raise ValueError(
                    "the value for 'visible_options' must be less or equal to the number of items in 'options'"
                    f" ({num_options})"
                )

        return instance


class LabelSelectionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.label_selection]
    visible_options: Optional[int] = Field(None, ge=LABEL_SELECTION_MIN_VISIBLE_OPTIONS)
    options: Optional[
        conlist(
            item_type=OptionSettings,
            min_length=LABEL_SELECTION_OPTIONS_MIN_ITEMS,
            max_length=settings.label_selection_options_max_items,
        )
    ] = None


# Multi-label selection question
class MultiLabelSelectionQuestionSettings(LabelSelectionQuestionSettings):
    type: Literal[QuestionType.multi_label_selection]
    options_order: OptionsOrder = OptionsOrder.natural


class MultiLabelSelectionQuestionSettingsCreate(LabelSelectionQuestionSettingsCreate):
    type: Literal[QuestionType.multi_label_selection]
    options_order: OptionsOrder = OptionsOrder.natural


class MultiLabelSelectionQuestionSettingsUpdate(LabelSelectionSettingsUpdate):
    type: Literal[QuestionType.multi_label_selection]
    options_order: Optional[OptionsOrder] = None

    __non_nullable_fields__ = {"options_order"}


# Ranking question
class RankingQuestionSettings(BaseModel):
    type: Literal[QuestionType.ranking]
    options: List[OptionSettings]


class RankingQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.ranking]
    options: conlist(
        item_type=OptionSettingsCreate,
        min_length=RANKING_OPTIONS_MIN_ITEMS,
        max_length=RANKING_OPTIONS_MAX_ITEMS,
    )


class RankingQuestionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.ranking]


# Span question
class SpanQuestionSettings(BaseModel):
    type: Literal[QuestionType.span]
    field: str
    options: List[OptionSettings]
    visible_options: Optional[int] = None
    # These attributes are read-only for now
    allow_overlapping: bool = Field(default=False, description="Allow spans overlapping")
    allow_character_annotation: bool = Field(default=True, description="Allow character-level annotation")


class SpanQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.span]
    field: FieldName
    options: conlist(
        item_type=OptionSettingsCreate,
        min_length=SPAN_OPTIONS_MIN_ITEMS,
        max_length=settings.span_options_max_items,
    )
    visible_options: Optional[int] = Field(None, ge=SPAN_MIN_VISIBLE_OPTIONS)
    allow_overlapping: bool = False

    @model_validator(mode="after")
    @classmethod
    def check_visible_options_value(cls, instance: "SpanQuestionSettingsCreate") -> "SpanQuestionSettingsCreate":
        visible_options = instance.visible_options
        if visible_options is not None:
            num_options = len(instance.options)
            if visible_options > num_options:
                raise ValueError(
                    "the value for 'visible_options' must be less or equal to the number of items in 'options'"
                    f" ({num_options})"
                )

        return instance


class SpanQuestionSettingsUpdate(UpdateSchema):
    type: Literal[QuestionType.span]
    options: Optional[
        conlist(
            item_type=OptionSettings,
            min_length=SPAN_OPTIONS_MIN_ITEMS,
            max_length=settings.span_options_max_items,
        )
    ] = None
    visible_options: Optional[int] = Field(None, ge=SPAN_MIN_VISIBLE_OPTIONS)
    allow_overlapping: Optional[bool] = None


QuestionSettings = Annotated[
    Union[
        TextQuestionSettings,
        RatingQuestionSettings,
        LabelSelectionQuestionSettings,
        MultiLabelSelectionQuestionSettings,
        RankingQuestionSettings,
        SpanQuestionSettings,
    ],
    Field(..., discriminator="type"),
]

QuestionName = Annotated[
    constr(
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

QuestionSettingsCreate = Annotated[
    Union[
        TextQuestionSettingsCreate,
        RatingQuestionSettingsCreate,
        LabelSelectionQuestionSettingsCreate,
        MultiLabelSelectionQuestionSettingsCreate,
        RankingQuestionSettingsCreate,
        SpanQuestionSettingsCreate,
    ],
    Field(discriminator="type"),
]

QuestionSettingsUpdate = Annotated[
    Union[
        TextQuestionSettingsUpdate,
        RatingQuestionSettingsUpdate,
        LabelSelectionSettingsUpdate,
        MultiLabelSelectionQuestionSettingsUpdate,
        RankingQuestionSettingsUpdate,
        SpanQuestionSettingsUpdate,
    ],
    Field(..., discriminator="type"),
]


class Question(BaseModel):
    id: UUID
    name: str
    title: str
    description: Optional[str] = None
    required: bool
    settings: QuestionSettings
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Questions(BaseModel):
    items: List[Question]


class QuestionCreate(BaseModel):
    name: QuestionName
    title: QuestionTitle
    description: Optional[QuestionDescription] = None
    required: Optional[bool] = None
    settings: QuestionSettingsCreate


class QuestionUpdate(UpdateSchema):
    title: Optional[QuestionTitle] = None
    description: Optional[QuestionDescription] = None
    settings: Optional[QuestionSettingsUpdate] = None

    __non_nullable_fields__ = {"title", "settings"}
