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
from argilla_v1.client.feedback.schemas.enums import FieldTypes
from argilla_v1.client.feedback.schemas.fields import TextField

from tests.pydantic_v1 import ValidationError


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a"},
            {"name": "a", "title": "A", "required": True, "settings": {"type": "text", "use_markdown": False}},
        ),
        (
            {"name": "a", "title": "b"},
            {"name": "a", "title": "b", "required": True, "settings": {"type": "text", "use_markdown": False}},
        ),
        (
            {"name": "a", "title": "b", "required": False},
            {"name": "a", "title": "b", "required": False, "settings": {"type": "text", "use_markdown": False}},
        ),
        (
            {"name": "a", "title": "b", "required": False, "use_markdown": True},
            {"name": "a", "title": "b", "required": False, "settings": {"type": "text", "use_markdown": True}},
        ),
    ],
)
def test_text_field(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    text_field = TextField(**schema_kwargs)
    assert text_field.type == FieldTypes.text
    assert text_field.server_settings == server_payload["settings"]
    assert text_field.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        ({}, ValidationError, "name\n  field required"),
        # The test case below won't match the full regex, as it will assume the type is QuestionType.text instead, only God knows why
        ({"name": "a", "type": "other"}, ValidationError, "type\n  unexpected value; permitted:"),
    ],
)
def test_text_field_errors(schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        TextField(**schema_kwargs)
