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

from typing import Any, Dict

import pytest
from argilla.client.feedback.schemas.fields import FieldSchema, TextField
from pydantic import ValidationError


def test_field_schema() -> None:
    schema = FieldSchema(name="completion-a")
    assert schema.id is None
    assert schema.name == "completion-a"
    assert schema.title == "Completion-a"
    assert schema.type is None
    assert schema.settings == {}


def test_field_schema_name_validation_error() -> None:
    with pytest.raises(ValidationError, match=r"name\n  string does not match regex"):
        FieldSchema(name="Completion-A")


@pytest.mark.parametrize(
    "schema_kwargs, expected_settings",
    [
        (
            {"name": "a", "title": "a", "required": True, "use_markdown": True},
            {"type": "text", "use_markdown": True},
        ),
        (
            {"name": "a", "title": "a", "required": True, "use_markdown": False},
            {"type": "text", "use_markdown": False},
        ),
    ],
)
def test_text_field(schema_kwargs: Dict[str, Any], expected_settings: Dict[str, Any]) -> None:
    assert TextField(**schema_kwargs).dict(include={"settings"})["settings"] == expected_settings
