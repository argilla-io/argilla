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
from typing import Any, Dict
from uuid import uuid4

import pytest
from argilla_v1.client.feedback.schemas.enums import FieldTypes
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.remote.fields import RemoteTextField
from argilla_v1.client.sdk.v1.datasets.models import FeedbackFieldModel


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
def test_remote_text_field(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    text_field = RemoteTextField(**schema_kwargs)
    assert text_field.type == FieldTypes.text
    assert text_field.server_settings == server_payload["settings"]
    assert text_field.to_server_payload() == server_payload

    local_text_field = text_field.to_local()
    assert isinstance(local_text_field, TextField)
    assert local_text_field.type == FieldTypes.text
    assert local_text_field.server_settings == server_payload["settings"]
    assert local_text_field.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackFieldModel(
            id=uuid4(),
            name="a",
            title="A",
            required=True,
            settings={"type": "text", "use_markdown": False},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackFieldModel(
            id=uuid4(),
            name="b",
            title="B",
            required=False,
            settings={"type": "text", "use_markdown": True},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_text_field_from_api(payload: FeedbackFieldModel) -> None:
    text_field = RemoteTextField.from_api(payload)
    assert text_field.type == FieldTypes.text
    assert text_field.server_settings == payload.settings
    assert text_field.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})
