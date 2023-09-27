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
    FloatMetadataFilter,
    FloatMetadataProperty,
    IntegerMetadataFilter,
    IntegerMetadataProperty,
    TermsMetadataFilter,
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
                # "visible_for_annotators": True,
                "settings": {"type": "terms", "values": ["a", "b", "c"]},
            },
        ),
        (
            {
                "name": "a",
                # "visible_for_annotators": False,
                "values": ["a", "b", "c"],
            },
            {
                "name": "a",
                "description": None,
                # "visible_for_annotators": False,
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
            "1 validation error for TermsMetadataProperty\nvalues\n  ensure this value has at least 1 items",
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
        # TODO: uncomment this unit tests case once min and max are optional
        # (
        #     {"name": "a", "description": "b"},
        #     {
        #         "name": "a",
        #         "description": "b",
        #         # "visible_for_annotators": True,
        #         "settings": {"type": "integer"},
        #     },
        # ),
        # (
        #     {
        #         "name": "a",
        #         # "visible_for_annotators": False,
        #         "max": 5,
        #     },
        #     {
        #         "name": "a",
        #         "description": None,
        #         # "visible_for_annotators": False,
        #         "settings": {"type": "integer", "max": 5},
        #     },
        # ),
        # (
        #     {"name": "a", "min": 5},
        #     {
        #         "name": "a",
        #         "description": None,
        #         # "visible_for_annotators": True,
        #         "settings": {"type": "integer", "min": 5},
        #     },
        # ),
        (
            {"name": "a", "min": 5, "max": 10},
            {
                "name": "a",
                "description": None,
                # "visible_for_annotators": True,
                "settings": {"type": "integer", "min": 5, "max": 10},
            },
        ),
    ],
)
def test_integer_metadata_property(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    metadata_property = IntegerMetadataProperty(**schema_kwargs)
    assert metadata_property.type == MetadataPropertyTypes.integer
    assert metadata_property.server_settings == server_payload["settings"]
    assert metadata_property.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        (
            {"name": "integer-metadata-property", "min": 5},
            ValidationError,
            "1 validation error for IntegerMetadataProperty\nmax\n  field required",
        ),
        (
            {"name": "integer-metadata-property", "max": 5},
            ValidationError,
            "1 validation error for IntegerMetadataProperty\nmin\n  field required",
        ),
        (
            {"name": "int-metadata-property", "min": 5, "max": 5},
            ValidationError,
            "1 validation error for IntegerMetadataProperty\n__root__\n  `IntegerMetadataProperty` with name=int-metadata-property cannot have `max` less or equal than `min`",
        ),
        (
            {"name": "int-metadata-property", "min": 6, "max": 6},
            ValidationError,
            "1 validation error for IntegerMetadataProperty\n__root__\n  `IntegerMetadataProperty` with name=int-metadata-property cannot have `max` less or equal than `min`",
        ),
    ],
)
def test_integer_metadata_property_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        IntegerMetadataProperty(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        # TODO: uncomment this unit tests case once min and max are optional
        # (
        #     {"name": "a", "description": "b"},
        #     {
        #         "name": "a",
        #         "description": "b",
        #         # "visible_for_annotators": True,
        #         "settings": {"type": "float"},
        #     },
        # ),
        # (
        #     {
        #         "name": "a",
        #         # "visible_for_annotators": False,
        #         "max": 5.0,
        #     },
        #     {
        #         "name": "a",
        #         "description": None,
        #         # "visible_for_annotators": False,
        #         "settings": {"type": "float", "max": 5.0},
        #     },
        # ),
        # (
        #     {"name": "a", "min": 5.0},
        #     {
        #         "name": "a",
        #         "description": None,
        #         # "visible_for_annotators": True,
        #         "settings": {"type": "float", "min": 5.0},
        #     },
        # ),
        (
            {"name": "a", "min": 5.0, "max": 10.0},
            {
                "name": "a",
                "description": None,
                # "visible_for_annotators": True,
                "settings": {"type": "float", "min": 5.0, "max": 10.0},
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
            {"name": "float-metadata-property", "min": 5.0},
            ValidationError,
            "1 validation error for FloatMetadataProperty\nmax\n  field required",
        ),
        (
            {"name": "float-metadata-property", "max": 5.0},
            ValidationError,
            "1 validation error for FloatMetadataProperty\nmin\n  field required",
        ),
        (
            {"name": "float-metadata-property", "min": 5.0, "max": 5.0},
            ValidationError,
            "1 validation error for FloatMetadataProperty\n__root__\n  `FloatMetadataProperty` with name=float-metadata-property cannot have `max` less or equal than `min`",
        ),
        (
            {"name": "float-metadata-property", "min": 6.0, "max": 5.0},
            ValidationError,
            "1 validation error for FloatMetadataProperty\n__root__\n  `FloatMetadataProperty` with name=float-metadata-property cannot have `max` less or equal than `min`",
        ),
    ],
)
def test_float_metadata_property_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        FloatMetadataProperty(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, query_string",
    [
        ({"name": "name", "values": ["a"]}, "name:a"),
        ({"name": "name-with-hyphen", "values": ["a", "b"]}, "name-with-hyphen:a,b"),
        ({"name": "name_with_underscore", "values": ["a", "b", "c"]}, "name_with_underscore:a,b,c"),
    ],
)
def test_terms_metadata_filter(schema_kwargs: Dict[str, Any], query_string: str) -> None:
    metadata_filter = TermsMetadataFilter(**schema_kwargs)
    assert metadata_filter.type == MetadataPropertyTypes.terms
    assert metadata_filter.query_string == query_string


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        (
            {"name": "terms-metadata-filter", "values": []},
            ValidationError,
            "1 validation error for TermsMetadataFilter\nvalues\n  ensure this value has at least 1 items",
        ),
        (
            {"name": "terms-metadata-filter", "values": ["a", "a"]},
            ValidationError,
            "1 validation error for TermsMetadataFilter\nvalues\n  `TermsMetadataFilter` with name=terms-metadata-filter cannot have repeated `values`",
        ),
    ],
)
def test_terms_metadata_filter_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        TermsMetadataFilter(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, query_string",
    [
        ({"name": "name", "le": 5}, 'name:{"le": 5}'),
        ({"name": "name", "ge": 5}, 'name:{"ge": 5}'),
        ({"name": "name", "le": 1, "ge": 5}, 'name:{"le": 1, "ge": 5}'),
        ({"name": "name", "le": 5, "ge": 5}, 'name:{"le": 5, "ge": 5}'),
    ],
)
def test_integer_metadata_filter(schema_kwargs: Dict[str, Any], query_string: str) -> None:
    metadata_filter = IntegerMetadataFilter(**schema_kwargs)
    assert metadata_filter.type == MetadataPropertyTypes.integer
    assert metadata_filter.query_string == query_string


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        (
            {"name": "int-metadata-filter"},
            ValueError,
            "1 validation error for IntegerMetadataFilter\n__root__\n  `IntegerMetadataFilter` with name=int-metadata-filter must have at least one of `le` or `ge`",
        ),
        (
            {"name": "int-metadata-filter", "le": 6, "ge": 5},
            ValidationError,
            "1 validation error for IntegerMetadataFilter\n__root__\n  `IntegerMetadataFilter` with name=int-metadata-filter cannot have `ge` less than `le`",
        ),
    ],
)
def test_integer_metadata_filter_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        IntegerMetadataFilter(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, query_string",
    [
        ({"name": "name", "le": 5.0}, 'name:{"le": 5.0}'),
        ({"name": "name", "ge": 5.0}, 'name:{"ge": 5.0}'),
        ({"name": "name", "le": 1.0, "ge": 5.0}, 'name:{"le": 1.0, "ge": 5.0}'),
        ({"name": "name", "le": 5.0, "ge": 5.0}, 'name:{"le": 5.0, "ge": 5.0}'),
    ],
)
def test_float_metadata_filter(schema_kwargs: Dict[str, Any], query_string: str) -> None:
    metadata_filter = FloatMetadataFilter(**schema_kwargs)
    assert metadata_filter.type == MetadataPropertyTypes.float
    assert metadata_filter.query_string == query_string


@pytest.mark.parametrize(
    "schema_kwargs, exception_cls, exception_message",
    [
        ({"name": "a b"}, ValidationError, "name\n  string does not match regex"),
        (
            {"name": "float-metadata-filter"},
            ValueError,
            "1 validation error for FloatMetadataFilter\n__root__\n  `FloatMetadataFilter` with name=float-metadata-filter must have at least one of `le` or `ge`",
        ),
        (
            {"name": "float-metadata-filter", "le": 6.0, "ge": 5.0},
            ValidationError,
            "1 validation error for FloatMetadataFilter\n__root__\n  `FloatMetadataFilter` with name=float-metadata-filter cannot have `ge` less than `le`",
        ),
    ],
)
def test_float_metadata_filter_errors(
    schema_kwargs: Dict[str, Any], exception_cls: Any, exception_message: str
) -> None:
    with pytest.raises(exception_cls, match=exception_message):
        FloatMetadataFilter(**schema_kwargs)
