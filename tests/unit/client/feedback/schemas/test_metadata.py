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
from argilla.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from pydantic import ValidationError


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "description": "b", "values": ["a", "b", "c"]},
            {
                "name": "a",
                "description": "b",
                "visible_for_annotators": True,
                "settings": {"type": "terms", "values": ["a", "b", "c"]},
            },
        ),
        (
            {"name": "a", "visible_for_annotators": False, "values": ["a", "b", "c"]},
            {
                "name": "a",
                "description": None,
                "visible_for_annotators": False,
                "settings": {"type": "terms", "values": ["a", "b", "c"]},
            },
        ),
    ],
)
def test_terms_metadata_property(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    metadata_property = TermsMetadataProperty(**schema_kwargs)
    assert metadata_property.type == MetadataPropertyTypes.terms
    assert metadata_property.server_settings == server_payload["settings"]
    assert metadata_property.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        (
            {"name": "terms-metadata-property", "values": []},
            ValidationError,
            "1 validation error for TermsMetadataProperty\nvalues\n  ensure this value has at least 2 items",
        ),
        (
            {"name": "terms-metadata-property", "values": ["just-one"]},
            ValidationError,
            "1 validation error for TermsMetadataProperty\nvalues\n  ensure this value has at least 2 items",
        ),
        (
            {"name": "terms-metadata-property", "values": ["a", "a"]},
            ValidationError,
            "1 validation error for TermsMetadataProperty\nvalues\n  `TermsMetadataProperty` with name=terms-metadata-property cannot have repeated `values`",
        ),
    ],
)
def test_terms_metadata_property_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        TermsMetadataProperty(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "description": "b"},
            {"name": "a", "description": "b", "visible_for_annotators": True, "settings": {"type": "integer"}},
        ),
        (
            {"name": "a", "visible_for_annotators": False, "lt": 5},
            {
                "name": "a",
                "description": None,
                "visible_for_annotators": False,
                "settings": {"type": "integer", "lt": 5},
            },
        ),
        (
            {"name": "a", "gt": 5},
            {
                "name": "a",
                "description": None,
                "visible_for_annotators": True,
                "settings": {"type": "integer", "gt": 5},
            },
        ),
        (
            {"name": "a", "gt": 5, "lt": 10},
            {
                "name": "a",
                "description": None,
                "visible_for_annotators": True,
                "settings": {"type": "integer", "gt": 5, "lt": 10},
            },
        ),
    ],
)
def test_int_metadata_property(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    metadata_property = IntegerMetadataProperty(**schema_kwargs)
    assert metadata_property.type == MetadataPropertyTypes.integer
    assert metadata_property.server_settings == server_payload["settings"]
    assert metadata_property.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        (
            {"name": "int-metadata-property", "lt": 5, "gt": 5},
            ValidationError,
            "1 validation error for IntMetadataProperty\n__root__\n  `IntMetadataProperty` with name=int-metadata-property cannot have `lt` less than `gt`",
        ),
        (
            {"name": "int-metadata-property", "lt": 5, "gt": 6},
            ValidationError,
            "1 validation error for IntMetadataProperty\n__root__\n  `IntMetadataProperty` with name=int-metadata-property cannot have `lt` less than `gt`",
        ),
    ],
)
def test_int_metadata_property_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        IntegerMetadataProperty(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "a", "description": "b"},
            {"name": "a", "description": "b", "visible_for_annotators": True, "settings": {"type": "float"}},
        ),
        (
            {"name": "a", "visible_for_annotators": False, "lt": 5.0},
            {
                "name": "a",
                "description": None,
                "visible_for_annotators": False,
                "settings": {"type": "float", "lt": 5.0},
            },
        ),
        (
            {"name": "a", "gt": 5.0},
            {
                "name": "a",
                "description": None,
                "visible_for_annotators": True,
                "settings": {"type": "float", "gt": 5.0},
            },
        ),
        (
            {"name": "a", "gt": 5.0, "lt": 10.0},
            {
                "name": "a",
                "description": None,
                "visible_for_annotators": True,
                "settings": {"type": "float", "gt": 5.0, "lt": 10.0},
            },
        ),
    ],
)
def test_float_metadata_property(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    metadata_property = FloatMetadataProperty(**schema_kwargs)
    assert metadata_property.type == MetadataPropertyTypes.float
    assert metadata_property.server_settings == server_payload["settings"]
    assert metadata_property.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        (
            {"name": "float-metadata-property", "lt": 5.0, "gt": 5.0},
            ValidationError,
            "1 validation error for FloatMetadataProperty\n__root__\n  `FloatMetadataProperty` with name=float-metadata-property cannot have `lt` less than `gt`",
        ),
        (
            {"name": "float-metadata-property", "lt": 5.0, "gt": 6.0},
            ValidationError,
            "1 validation error for FloatMetadataProperty\n__root__\n  `FloatMetadataProperty` with name=float-metadata-property cannot have `lt` less than `gt`",
        ),
    ],
)
def test_float_metadata_property_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        FloatMetadataProperty(**schema_kwargs)
