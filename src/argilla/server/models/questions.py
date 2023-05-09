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
from enum import Enum
from typing import Any, List, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Annotated, Literal

from argilla.client.datasets import Dataset
from argilla.server.database import Base


def default_inserted_at(context):
    return context.get_current_parameters()["inserted_at"]


class QuestionType(str, Enum):
    text = "text"
    rating = "rating"


class ResponseValue(BaseModel):
    value: Any


class BaseQuestionSettings(BaseModel):
    def check_response(self, response: ResponseValue):
        pass


class TextQuestionSettings(BaseQuestionSettings):
    type: Literal[QuestionType.text]

    def check_response(self, response: ResponseValue):
        if not isinstance(response.value, str):
            raise ValueError(f"Expected text value, found {type(response.value)}")


class RatingQuestionSettingsOption(BaseModel):
    value: int


class RatingQuestionSettings(BaseQuestionSettings):
    type: Literal[QuestionType.rating]
    options: List[RatingQuestionSettingsOption]

    @property
    def option_values(self) -> List[int]:
        return [option.value for option in self.options]

    def check_response(self, response: ResponseValue):
        if response.value not in self.option_values:
            raise ValueError(f"{response.value!r} is not a valid option.\nValid options are: {self.option_values!r}")


QuestionSettings = Annotated[Union[TextQuestionSettings, RatingQuestionSettings], Field(..., discriminator="type")]


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    required: Mapped[bool] = mapped_column(default=False)
    settings: Mapped[dict] = mapped_column(JSON, default={})
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"))

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="questions")

    def __repr__(self):
        return (
            f"Question(id={str(self.id)!r}, name={self.name!r}, required={self.required!r}, "
            f"dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )
