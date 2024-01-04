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

from abc import ABC, abstractmethod
from typing import Any, Dict, Literal, Optional

from argilla.client.feedback.schemas.enums import FieldTypes
from argilla.client.feedback.schemas.validators import title_must_have_value
from argilla.pydantic_v1 import BaseModel, Extra, Field, validator


class FieldSchema(BaseModel, ABC):
    """Base schema for the `FeedbackDataset` fields.

    Args:
        name: The name of the field. This is the only required field.
        title: The title of the field. If not provided, it will be capitalized from
            the `name` field. And its what will be shown in the UI.
        required: Whether the field is required or not. Defaults to True. Note that at
            least one field must be required.
        type: The type of the field. Defaults to None, and ideally it should be defined
            in the class inheriting from this one to be able to use a discriminated union
            based on the `type` field.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one, as they will have the `type` field already defined, and ensured
        to be supported by Argilla.
    """

    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    title: Optional[str] = None
    required: bool = True
    type: Optional[FieldTypes] = Field(..., allow_mutation=False)

    _title_must_have_value = validator("title", always=True, allow_reuse=True)(title_must_have_value)

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"type"}

    @property
    @abstractmethod
    def server_settings(self) -> Dict[str, Any]:
        """Abstract property that should be implemented by the classes that inherit from
        this one, and that will be used to create the `FeedbackDataset` in Argilla.
        """
        ...

    def to_server_payload(self) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a field in the `FeedbackDataset`.
        """
        return {
            "name": self.name,
            "title": self.title,
            "required": self.required,
            "settings": self.server_settings,
        }


class TextField(FieldSchema):
    """Schema for the `FeedbackDataset` text fields, which are the ones that will
    require a text to be defined as part of the record.

    Args:
        type: The type of the field. Defaults to 'text' and cannot/shouldn't be
            modified.
        use_markdown: Whether the field should be rendered using markdown or not.
            Defaults to False.

    Examples:
        >>> from argilla.client.feedback.schemas.fields import TextField
        >>> TextField(name="text_field", title="Text Field")
    """

    type: Literal[FieldTypes.text] = Field(FieldTypes.text.value, allow_mutation=False)
    use_markdown: bool = False

    @property
    def server_settings(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "use_markdown": self.use_markdown,
        }
