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
from argilla_v1.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)
from argilla_v1.client.sdk.v1.datasets.models import FeedbackMetadataPropertyModel


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "terms-metadata"},
            {
                "name": "terms-metadata",
                "title": "terms-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "terms"},
            },
        ),
        (
            {"name": "terms-metadata", "title": "alt-title"},
            {
                "name": "terms-metadata",
                "title": "alt-title",
                "visible_for_annotators": True,
                "settings": {"type": "terms"},
            },
        ),
        (
            {"name": "terms-metadata", "visible_for_annotators": False},
            {
                "name": "terms-metadata",
                "title": "terms-metadata",
                "visible_for_annotators": False,
                "settings": {"type": "terms"},
            },
        ),
        (
            {"name": "terms-metadata", "values": ["a"]},
            {
                "name": "terms-metadata",
                "title": "terms-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "terms", "values": ["a"]},
            },
        ),
        (
            {"name": "terms-metadata", "values": ["a", "b", "c"]},
            {
                "name": "terms-metadata",
                "title": "terms-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "terms", "values": ["a", "b", "c"]},
            },
        ),
    ],
)
def test_remote_terms_metadata_property(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    text_field = RemoteTermsMetadataProperty(**schema_kwargs)
    assert text_field.type == MetadataPropertyTypes.terms
    assert text_field.server_settings == server_payload["settings"]
    assert text_field.to_server_payload() == server_payload

    local_text_field = text_field.to_local()
    assert isinstance(local_text_field, TermsMetadataProperty)
    assert local_text_field.type == MetadataPropertyTypes.terms
    assert local_text_field.server_settings == server_payload["settings"]
    assert local_text_field.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="terms-metadata",
            title="alt-title",
            visible_for_annotators=True,
            settings={"type": "terms"},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="terms-metadata",
            title="terms-metadata",
            visible_for_annotators=False,
            settings={"type": "terms", "values": ["a", "b", "c"]},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_terms_metadata_property_from_api(payload: FeedbackMetadataPropertyModel) -> None:
    text_field = RemoteTermsMetadataProperty.from_api(payload)
    assert text_field.type == MetadataPropertyTypes.terms
    assert text_field.server_settings == payload.settings
    assert text_field.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "int-metadata"},
            {
                "name": "int-metadata",
                "title": "int-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "integer"},
            },
        ),
        (
            {"name": "int-metadata", "title": "alt-title"},
            {
                "name": "int-metadata",
                "title": "alt-title",
                "visible_for_annotators": True,
                "settings": {"type": "integer"},
            },
        ),
        (
            {"name": "int-metadata", "visible_for_annotators": False},
            {
                "name": "int-metadata",
                "title": "int-metadata",
                "visible_for_annotators": False,
                "settings": {"type": "integer"},
            },
        ),
        (
            {"name": "int-metadata", "min": 0},
            {
                "name": "int-metadata",
                "title": "int-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "integer", "min": 0},
            },
        ),
        (
            {"name": "int-metadata", "max": 10},
            {
                "name": "int-metadata",
                "title": "int-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "integer", "max": 10},
            },
        ),
        (
            {"name": "int-metadata", "min": 0, "max": 10},
            {
                "name": "int-metadata",
                "title": "int-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "integer", "min": 0, "max": 10},
            },
        ),
    ],
)
def test_remote_integer_metadata_property(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    text_field = RemoteIntegerMetadataProperty(**schema_kwargs)
    assert text_field.type == MetadataPropertyTypes.integer
    assert text_field.server_settings == server_payload["settings"]
    assert text_field.to_server_payload() == server_payload

    local_text_field = text_field.to_local()
    assert isinstance(local_text_field, IntegerMetadataProperty)
    assert local_text_field.type == MetadataPropertyTypes.integer
    assert local_text_field.server_settings == server_payload["settings"]
    assert local_text_field.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="int-metadata",
            title="alt-title",
            visible_for_annotators=True,
            settings={"type": "integer"},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="int-metadata",
            title="int-metadata",
            visible_for_annotators=True,
            settings={"type": "integer", "min": 0},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="int-metadata",
            title="int-metadata",
            visible_for_annotators=False,
            settings={"type": "integer", "min": 0, "max": 10},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_integer_metadata_property_from_api(payload: FeedbackMetadataPropertyModel) -> None:
    text_field = RemoteIntegerMetadataProperty.from_api(payload)
    assert text_field.type == MetadataPropertyTypes.integer
    assert text_field.server_settings == payload.settings
    assert text_field.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {"name": "float-metadata"},
            {
                "name": "float-metadata",
                "title": "float-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "float"},
            },
        ),
        (
            {"name": "float-metadata", "title": "alt-title"},
            {
                "name": "float-metadata",
                "title": "alt-title",
                "visible_for_annotators": True,
                "settings": {"type": "float"},
            },
        ),
        (
            {"name": "float-metadata", "visible_for_annotators": False},
            {
                "name": "float-metadata",
                "title": "float-metadata",
                "visible_for_annotators": False,
                "settings": {"type": "float"},
            },
        ),
        (
            {"name": "float-metadata", "min": 0.0},
            {
                "name": "float-metadata",
                "title": "float-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "float", "min": 0.0},
            },
        ),
        (
            {"name": "float-metadata", "max": 10.0},
            {
                "name": "float-metadata",
                "title": "float-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "float", "max": 10.0},
            },
        ),
        (
            {"name": "float-metadata", "min": 0.0, "max": 10.0},
            {
                "name": "float-metadata",
                "title": "float-metadata",
                "visible_for_annotators": True,
                "settings": {"type": "float", "min": 0.0, "max": 10.0},
            },
        ),
    ],
)
def test_remote_float_metadata_property(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    text_field = RemoteFloatMetadataProperty(**schema_kwargs)
    assert text_field.type == MetadataPropertyTypes.float
    assert text_field.server_settings == server_payload["settings"]
    assert text_field.to_server_payload() == server_payload

    local_text_field = text_field.to_local()
    assert isinstance(local_text_field, FloatMetadataProperty)
    assert local_text_field.type == MetadataPropertyTypes.float
    assert local_text_field.server_settings == server_payload["settings"]
    assert local_text_field.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="float-metadata",
            title="alt-title",
            visible_for_annotators=True,
            settings={"type": "float"},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="float-metadata",
            title="float-metadata",
            visible_for_annotators=True,
            settings={"type": "float", "min": 0.0},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackMetadataPropertyModel(
            id=uuid4(),
            name="float-metadata",
            title="float-metadata",
            visible_for_annotators=False,
            settings={"type": "float", "min": 0.0, "max": 10.0},
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_float_metadata_property_from_api(payload: FeedbackMetadataPropertyModel) -> None:
    text_field = RemoteFloatMetadataProperty.from_api(payload)
    assert text_field.type == MetadataPropertyTypes.float
    assert text_field.server_settings == payload.settings
    assert text_field.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})
