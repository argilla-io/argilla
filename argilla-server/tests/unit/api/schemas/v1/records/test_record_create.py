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

from dataclasses import fields
from typing import Any

import pytest

from argilla_server.api.schemas.v1.chat import ChatFieldValue
from argilla_server.api.schemas.v1.records import RecordCreate


class TestRecordCreate:
    def test_record_create_with_empty_string_field(self):
        record_create = RecordCreate(fields={"field": ""})
        assert record_create.fields == {"field": ""}

    def test_record_create_with_empty_list_field(self):
        record_create = RecordCreate(fields={"field": []})
        assert record_create.fields == {"field": []}

    def test_record_create_with_empty_dict_field(self):
        record_create = RecordCreate(fields={"field": {}})
        assert record_create.fields == {"field": {}}

    def test_record_create_with_none(self):
        record_create = RecordCreate(fields={"field": None})
        assert record_create.fields == {"field": None}

    def test_record_create_with_string_field(self):
        record_create = RecordCreate(fields={"field": "text"})
        assert record_create.fields == {"field": "text"}

    def test_record_create_with_dict_field(self):
        record_create = RecordCreate(fields={"field": {"key": "value"}})
        assert record_create.fields == {"field": {"key": "value"}}

    def test_record_create_with_chat_field_object(self):
        record_create = RecordCreate(
            fields={
                "field": [
                    ChatFieldValue(role="user", content="Hello, how are you?"),
                    ChatFieldValue(role="bot", content="I'm fine, thank you."),
                ]
            }
        )

        assert record_create.fields == {
            "field": [
                ChatFieldValue(role="user", content="Hello, how are you?"),
                ChatFieldValue(role="bot", content="I'm fine, thank you."),
            ]
        }

        assert record_create.fields == {
            "field": [
                ChatFieldValue(role="user", content="Hello, how are you?"),
                ChatFieldValue(role="bot", content="I'm fine, thank you."),
            ]
        }

    def test_record_create_with_chat_field(self):
        record_create = RecordCreate(
            fields={
                "field": [
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "bot", "content": "I'm fine, thank you."},
                ]
            }
        )

        assert record_create.fields == {
            "field": [
                ChatFieldValue(role="user", content="Hello, how are you?"),
                ChatFieldValue(role="bot", content="I'm fine, thank you."),
            ]
        }

    @pytest.mark.parametrize(
        "wrong_value",
        [
            {},
            {"role": "user"},
            {"content": "Hello, how are you?"},
            {"wrong": "value"},
            {"role": "user", "other": "Hello, how are you?"},
            {"content": "Hello, how are you?", "other": "user"},
            ["user", "Hello, how are you?"],
        ],
    )
    def test_record_create_with_wrong_chat_field(self, wrong_value: dict):
        with pytest.raises(ValueError):
            RecordCreate(fields={"field": [wrong_value]})

    def test_record_create_with_exceeded_chat_messages(self):
        with pytest.raises(ValueError):
            RecordCreate(
                fields={
                    "field": [
                        {"role": "user", "content": "Hello, how are you?"},
                        {"role": "bot", "content": "I'm fine, thank you."},
                    ]
                    * 1000
                }
            )
