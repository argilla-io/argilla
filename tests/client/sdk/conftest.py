#  coding=utf-8
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

import pytest

import rubrix as rb
from rubrix._constants import DEFAULT_API_KEY
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
)
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
)


class Helpers:
    def remove_key(self, schema: dict, key: str):
        """Removes a key key from a model schema"""
        if key in schema:
            del schema[key]
        for value in schema.values():
            if isinstance(value, dict):
                self.remove_key(value, key)
        return schema

    def remove_description(self, schema: dict):
        """Removes the 'description' key from a model schema. We do not care about the doc strings."""
        return self.remove_key(schema, key="description")

    def remove_pattern(self, schema: dict):
        return self.remove_key(schema, key="pattern")

    def are_compatible_api_schemas(self, client_schema: dict, server_schema: dict):
        if (
            not client_schema["properties"].items()
            <= server_schema["properties"].items()
        ):
            assert client_schema["properties"] == server_schema["properties"]
        return True


@pytest.fixture(scope="session")
def helpers():
    return Helpers()


@pytest.fixture
def sdk_client(mocked_client, monkeypatch):
    client = AuthenticatedClient(
        base_url="http://localhost:6900", token=DEFAULT_API_KEY
    )
    monkeypatch.setattr(client, "__httpx__", mocked_client)
    return client


@pytest.fixture
def bulk_textclass_data():
    explanation = {
        "text": [rb.TokenAttributions(token="test", attributions={"test": 0.5})]
    }
    records = [
        rb.TextClassificationRecord(
            text="test",
            prediction=[("test", 0.5)],
            prediction_agent="agent",
            annotation="test1",
            annotation_agent="agent",
            multi_label=False,
            explanation=explanation,
            id=i,
            metadata={"mymetadata": "str"},
            event_timestamp=datetime(2020, 1, 1),
            status="Validated",
        )
        for i in range(3)
    ]

    return TextClassificationBulkData(
        records=[CreationTextClassificationRecord.from_client(rec) for rec in records],
        tags={"Mytag": "tag"},
        metadata={"MyMetadata": 5},
    )


@pytest.fixture
def bulk_text2text_data():
    records = [
        rb.Text2TextRecord(
            text="test",
            prediction=[("prueba", 0.5), ("intento", 0.5)],
            prediction_agent="agent",
            annotation="prueba",
            annotation_agent="agent",
            id=i,
            metadata={"mymetadata": "str"},
            event_timestamp=datetime(2020, 1, 1),
            status="Validated",
        )
        for i in range(3)
    ]

    return Text2TextBulkData(
        records=[CreationText2TextRecord.from_client(rec) for rec in records],
        tags={"Mytag": "tag"},
        metadata={"MyMetadata": 5},
    )


@pytest.fixture
def bulk_tokenclass_data():
    records = [
        rb.TokenClassificationRecord(
            text="a raw text",
            tokens=["a", "raw", "text"],
            prediction=[("test", 2, 5, 0.9)],
            prediction_agent="agent",
            annotation=[("test", 2, 5)],
            annotation_agent="agent",
            id=i,
            metadata={"mymetadata": "str"},
            event_timestamp=datetime(2020, 1, 1),
            status="Validated",
        )
        for i in range(3)
    ]

    return TokenClassificationBulkData(
        records=[CreationTokenClassificationRecord.from_client(rec) for rec in records],
        tags={"Mytag": "tag"},
        metadata={"MyMetadata": 5},
    )
