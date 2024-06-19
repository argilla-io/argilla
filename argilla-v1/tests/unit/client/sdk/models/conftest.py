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
from typing import Any, Dict, List

import pytest

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

    def are_compatible_api_schemas(self, client_schema: dict, server_schema: dict) -> bool:
        def check_schema_props(client_props: dict, server_props: dict) -> bool:
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
                    if isinstance(definition, dict) and isinstance(server_props[name], dict):
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

    def _expands_schema(self, props: Dict[str, Any], definitions: List[Dict[str, Any]]) -> Dict[str, Any]:
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
def helpers() -> Helpers:
    return Helpers()
