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
import logging
from datetime import datetime
from typing import Any, Dict, List

import argilla as ar
import pytest
from argilla._constants import DEFAULT_API_KEY
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
)
from argilla.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from argilla.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
)

LOGGER = logging.getLogger(__name__)


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
        def check_schema_props(client_props, server_props):
            different_props = []
            for name, definition in client_props.items():
                if name == "type":
                    continue
                if name not in server_props:
                    LOGGER.warning(
                        f"Client property {name} not found in server properties. " "Make sure your API compatibility"
                    )
                    different_props.append(name)
                    continue
                elif definition != server_props[name]:
                    if not check_schema_props(definition, server_props[name]):
                        return False
            return len(different_props) < len(client_props) / 2

        client_props = self._expands_schema(
            client_schema["properties"],
            client_schema.get("definitions", {}),
        )
        server_props = self._expands_schema(
            server_schema["properties"],
            server_schema.get("definitions", {}),
        )

        if client_props == server_props:
            return True

        return check_schema_props(client_props, server_props)

    def _expands_schema(
        self,
        props: Dict[str, Any],
        definitions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        new_schema = {}
        for name, definition in props.items():
            if "$ref" in definition:
                ref = definition["$ref"]
                ref_def = definitions[ref.replace("#/definitions/", "")]
                field_props = ref_def.get("properties", ref_def)
                expanded_props = self._expands_schema(field_props, definitions)
                new_schema[name] = expanded_props.get("properties", expanded_props)
            elif "items" in definition and "$ref" in definition["items"]:
                ref = definition["items"]["$ref"]
                ref_def = definitions[ref.replace("#/definitions/", "")]
                field_props = ref_def.get("properties", ref_def)
                expanded_props = self._expands_schema(field_props, definitions)
                definition["items"] = expanded_props.get("properties", expanded_props)
                new_schema[name] = definition
            elif "additionalProperties" in definition and "$ref" in definition.get("additionalProperties", {}):
                additionalProperties_refs = self._expands_schema(
                    {name: definition["additionalProperties"]},
                    definitions=definitions,
                )
                new_schema.update(additionalProperties_refs)
            elif "allOf" in definition:
                allOf_expanded = [
                    self._expands_schema(
                        definitions[def_["$ref"].replace("#/definitions/", "")].get("properties", {}),
                        definitions,
                    )
                    for def_ in definition["allOf"]
                    if "$ref" in def_
                ]
                if len(allOf_expanded) == 1:
                    new_schema[name] = allOf_expanded[0]
                else:
                    new_schema[name] = allOf_expanded
            else:
                new_schema[name] = definition
        return new_schema


@pytest.fixture(scope="session")
def helpers():
    return Helpers()


@pytest.fixture
def sdk_client(mocked_client, monkeypatch):
    client = AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY)
    monkeypatch.setattr(client, "__httpx__", mocked_client)
    return client


@pytest.fixture
def bulk_textclass_data():
    explanation = {"text": [ar.TokenAttributions(token="test", attributions={"test": 0.5})]}
    records = [
        ar.TextClassificationRecord(
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
        ar.Text2TextRecord(
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
        ar.TokenClassificationRecord(
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
