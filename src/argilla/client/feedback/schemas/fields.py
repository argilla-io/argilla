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

from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field, root_validator, validator

from argilla.client.feedback.schemas.validators import title_must_have_value

FieldTypes = Literal["text"]


class FieldSchema(BaseModel):
    """Base schema for the `FeedbackDataset` fields.

    Args:
        id: The ID of the field in Argilla. Defaults to None, and is automatically
            fulfilled internally once the field is pushed to Argilla.
        name: The name of the field. This is the only required field.
        title: The title of the field. If not provided, it will be capitalized from
            the `name` field. And its what will be shown in the UI.
        required: Whether the field is required or not. Defaults to True. Note that at
            least one field must be required.
        type: The type of the field. Defaults to None, and ideally it should be defined
            in the class inheriting from this one to be able to use a discriminated union
            based on the `type` field.
        settings: The settings of the field. Defaults to an empty dict, and it is
            automatically fulfilled internally before the field is pushed to Argilla,
            as the `settings` is part of the payload that will be sent to Argilla.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one, as they will have the `type` field already defined, and ensured
        to be supported by Argilla.
    """

    id: Optional[UUID] = None
    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    title: Optional[str] = None
    required: bool = True
    type: Optional[FieldTypes] = None
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    _title_must_have_value = validator("title", always=True, allow_reuse=True)(title_must_have_value)

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"id", "type"}


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

    type: Literal["text"] = "text"
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        values["settings"]["use_markdown"] = values.get("use_markdown", False)
        return values
