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

from fastapi import Body

from argilla_server.api.schemas.v1.questions import QuestionName
from argilla_server.enums import ResponseStatus
from pydantic import BaseModel, Field, StrictInt, StrictStr, root_validator, ConfigDict, model_validator

RESPONSES_BULK_CREATE_MIN_ITEMS = 1
RESPONSES_BULK_CREATE_MAX_ITEMS = 100

SPAN_QUESTION_RESPONSE_VALUE_MAX_ITEMS = 10_000

SPAN_QUESTION_RESPONSE_VALUE_ITEM_START_GREATER_THAN_OR_EQUAL = 0
SPAN_QUESTION_RESPONSE_VALUE_ITEM_END_GREATER_THAN_OR_EQUAL = 1

IMAGE_ANNOTATION_QUESTION_RESPONSE_VALUE_MAX_ITEMS = 10_000
IMAGE_ANNOTATION_MAX_HOLES_PER_SHAPE = 10


class RankingQuestionResponseValueItem(BaseModel):
    value: str
    rank: Optional[int] = None


class SpanQuestionResponseValueItem(BaseModel):
    label: str
    start: int = Field(..., ge=SPAN_QUESTION_RESPONSE_VALUE_ITEM_START_GREATER_THAN_OR_EQUAL)
    end: int = Field(..., ge=SPAN_QUESTION_RESPONSE_VALUE_ITEM_END_GREATER_THAN_OR_EQUAL)

    @model_validator(mode="after")
    @classmethod
    def check_start_and_end(cls, instance: "SpanQuestionResponseValueItem") -> "SpanQuestionResponseValueItem":
        start, end = instance.start, instance.end

        if start is not None and end is not None and end <= start:
            raise ValueError("span question response value 'end' must have a value greater than 'start'")

        return instance


class ImageAnnotationHole(BaseModel):
    """Hole/exclusion within an image annotation shape"""

    points: List[List[float]] = Field(..., description="Coordinates in [[x1,y1], [x2,y2], ...] format")
    shape_type: str = Field(..., description="Shape type: rectangle, polygon, circle, line, point")
    flags: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @model_validator(mode="after")
    @classmethod
    def check_hole_points_format(cls, instance: "ImageAnnotationHole") -> "ImageAnnotationHole":
        points = instance.points
        shape_type = instance.shape_type

        if not points:
            raise ValueError("hole points cannot be empty")

        # Validate each point has exactly 2 coordinates [x, y]
        for point in points:
            if len(point) != 2:
                raise ValueError(f"Each hole point must have exactly 2 coordinates [x, y], got {len(point)}")

        # Shape-specific validations for holes
        if shape_type == "rectangle" and len(points) != 2:
            raise ValueError("rectangle hole requires exactly 2 points (top-left and bottom-right)")
        elif shape_type == "point" and len(points) != 1:
            raise ValueError("point hole requires exactly 1 point")
        elif shape_type == "line" and len(points) < 2:
            raise ValueError("line hole requires at least 2 points")
        elif shape_type == "polygon" and len(points) < 3:
            raise ValueError("polygon hole requires at least 3 points")
        elif shape_type == "circle" and len(points) != 2:
            raise ValueError("circle hole requires exactly 2 points (center and edge)")

        return instance


class ImageAnnotationQuestionResponseValueItem(BaseModel):
    """Image annotation in labelme format"""

    label: str
    points: List[List[float]] = Field(..., description="Coordinates in [[x1,y1], [x2,y2], ...] format")
    shape_type: str = Field(..., description="Shape type: rectangle, polygon, circle, line, point")
    group_id: Optional[int] = None
    flags: Optional[Dict[str, Any]] = Field(default_factory=dict)
    holes: Optional[List[ImageAnnotationHole]] = Field(default=None, description="Holes/exclusions within the shape")

    @model_validator(mode="after")
    @classmethod
    def check_points_format(
        cls, instance: "ImageAnnotationQuestionResponseValueItem"
    ) -> "ImageAnnotationQuestionResponseValueItem":
        points = instance.points
        shape_type = instance.shape_type
        holes = instance.holes

        if not points:
            raise ValueError("points cannot be empty")

        # Validate each point has exactly 2 coordinates [x, y]
        for point in points:
            if len(point) != 2:
                raise ValueError(f"Each point must have exactly 2 coordinates [x, y], got {len(point)}")

        # Shape-specific validations
        if shape_type == "rectangle" and len(points) != 2:
            raise ValueError("rectangle shape requires exactly 2 points (top-left and bottom-right)")
        elif shape_type == "point" and len(points) != 1:
            raise ValueError("point shape requires exactly 1 point")
        elif shape_type == "line" and len(points) < 2:
            raise ValueError("line shape requires at least 2 points")
        elif shape_type == "polygon" and len(points) < 3:
            raise ValueError("polygon shape requires at least 3 points")
        elif shape_type == "circle" and len(points) != 2:
            raise ValueError("circle shape requires exactly 2 points (center and edge)")

        # Validate holes if present
        if holes is not None:
            if len(holes) > IMAGE_ANNOTATION_MAX_HOLES_PER_SHAPE:
                raise ValueError(
                    f"Maximum {IMAGE_ANNOTATION_MAX_HOLES_PER_SHAPE} holes allowed per shape, got {len(holes)}"
                )

            # Validate geometric containment of holes within parent shape
            cls._validate_holes_containment(points, shape_type, holes)

        return instance

    @staticmethod
    def _validate_holes_containment(
        parent_points: List[List[float]], parent_shape_type: str, holes: List[ImageAnnotationHole]
    ) -> None:
        """Validate that all holes are geometrically contained within the parent shape"""
        # Get parent bounding box
        parent_xs = [p[0] for p in parent_points]
        parent_ys = [p[1] for p in parent_points]
        parent_min_x, parent_max_x = min(parent_xs), max(parent_xs)
        parent_min_y, parent_max_y = min(parent_ys), max(parent_ys)

        # Check each hole
        for i, hole in enumerate(holes):
            hole_xs = [p[0] for p in hole.points]
            hole_ys = [p[1] for p in hole.points]
            hole_min_x, hole_max_x = min(hole_xs), max(hole_xs)
            hole_min_y, hole_max_y = min(hole_ys), max(hole_ys)

            # Bounding box containment check
            if not (
                parent_min_x <= hole_min_x
                and hole_max_x <= parent_max_x
                and parent_min_y <= hole_min_y
                and hole_max_y <= parent_max_y
            ):
                raise ValueError(f"Hole {i+1} is not fully contained within the parent shape bounds")

            # Additional check: all hole points must be within parent bounds
            for point in hole.points:
                if not (parent_min_x <= point[0] <= parent_max_x and parent_min_y <= point[1] <= parent_max_y):
                    raise ValueError(f"Hole {i+1} has points outside the parent shape bounds")


RankingQuestionResponseValue = List[RankingQuestionResponseValueItem]
SpanQuestionResponseValue = Annotated[
    List[SpanQuestionResponseValueItem], Field(..., max_length=SPAN_QUESTION_RESPONSE_VALUE_MAX_ITEMS)
]
ImageAnnotationQuestionResponseValue = Annotated[
    List[ImageAnnotationQuestionResponseValueItem],
    Field(..., max_length=IMAGE_ANNOTATION_QUESTION_RESPONSE_VALUE_MAX_ITEMS),
]
MultiLabelSelectionQuestionResponseValue = List[str]
RatingQuestionResponseValue = StrictInt
TextAndLabelSelectionQuestionResponseValue = StrictStr

ResponseValueTypes = Union[
    SpanQuestionResponseValue,
    ImageAnnotationQuestionResponseValue,
    RankingQuestionResponseValue,
    MultiLabelSelectionQuestionResponseValue,
    RatingQuestionResponseValue,
    TextAndLabelSelectionQuestionResponseValue,
]


class ResponseValue(BaseModel):
    value: Any


class ResponseValueCreate(BaseModel):
    value: ResponseValueTypes

    model_config = ConfigDict(coerce_numbers_to_str=True)


class ResponseValueUpdate(BaseModel):
    value: ResponseValueTypes

    model_config = ConfigDict(coerce_numbers_to_str=True)


ResponseValues = Dict[str, ResponseValue]
ResponseValuesCreate = Dict[QuestionName, ResponseValueCreate]
ResponseValuesUpdate = Dict[QuestionName, ResponseValueUpdate]


class Response(BaseModel):
    id: UUID
    values: Optional[ResponseValues] = None
    status: ResponseStatus
    record_id: UUID
    user_id: UUID
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseCreate(BaseModel):
    values: Optional[ResponseValuesCreate] = None
    status: ResponseStatus


class ResponseFilterScope(BaseModel):
    entity: Literal["response"]
    question: Optional[QuestionName] = None
    property: Optional[Literal["status"]] = None


class SubmittedResponseUpdate(BaseModel):
    values: ResponseValuesUpdate
    status: Literal[ResponseStatus.submitted]


class DiscardedResponseUpdate(BaseModel):
    values: Optional[ResponseValuesUpdate] = None
    status: Literal[ResponseStatus.discarded]


class DraftResponseUpdate(BaseModel):
    values: Optional[ResponseValuesUpdate] = None
    status: Literal[ResponseStatus.draft]


ResponseUpdate = Annotated[
    Union[SubmittedResponseUpdate, DiscardedResponseUpdate, DraftResponseUpdate],
    Body(..., discriminator="status"),
]


class SubmittedResponseUpsert(BaseModel):
    values: ResponseValuesUpdate
    status: Literal[ResponseStatus.submitted]
    record_id: UUID


class DiscardedResponseUpsert(BaseModel):
    values: Optional[ResponseValuesUpdate] = None
    status: Literal[ResponseStatus.discarded]
    record_id: UUID


class DraftResponseUpsert(BaseModel):
    values: Optional[ResponseValuesUpdate] = None
    status: Literal[ResponseStatus.draft]
    record_id: UUID


ResponseUpsert = Annotated[
    Union[SubmittedResponseUpsert, DiscardedResponseUpsert, DraftResponseUpsert],
    Body(..., discriminator="status"),
]


class ResponsesBulkCreate(BaseModel):
    items: List[ResponseUpsert] = Field(
        ...,
        min_length=RESPONSES_BULK_CREATE_MIN_ITEMS,
        max_length=RESPONSES_BULK_CREATE_MAX_ITEMS,
    )


class ResponseBulkError(BaseModel):
    detail: str


class ResponseBulk(BaseModel):
    item: Optional[Response] = None
    error: Optional[ResponseBulkError] = None


class ResponsesBulk(BaseModel):
    items: List[ResponseBulk]


class UserDraftResponseCreate(BaseModel):
    user_id: UUID
    values: ResponseValuesCreate
    status: Literal[ResponseStatus.draft]


class UserDiscardedResponseCreate(BaseModel):
    user_id: UUID
    values: Optional[ResponseValuesCreate] = None
    status: Literal[ResponseStatus.discarded]


class UserSubmittedResponseCreate(BaseModel):
    user_id: UUID
    values: ResponseValuesCreate
    status: Literal[ResponseStatus.submitted]


UserResponseCreate = Annotated[
    Union[UserSubmittedResponseCreate, UserDraftResponseCreate, UserDiscardedResponseCreate],
    Field(discriminator="status"),
]
