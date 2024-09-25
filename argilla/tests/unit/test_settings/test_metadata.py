# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import argilla as rg
from argilla._models import MetadataFieldModel, TermsMetadataPropertySettings


class TestMetadata:
    def test_create_metadata_terms(self):
        property = rg.TermsMetadataProperty(
            title="A metadata property", name="metadata", options=["option1", "option2"]
        )

        assert property._model.type == "terms"
        assert property.title == "A metadata property"
        assert property.name == "metadata"
        assert property.visible_for_annotators is True
        assert property.options == ["option1", "option2"]

        assert property.api_model().model_dump() == {
            "id": None,
            "dataset_id": None,
            "name": "metadata",
            "settings": {"type": "terms", "values": ["option1", "option2"], "visible_for_annotators": True},
            "title": "A metadata property",
            "type": "terms",
            "visible_for_annotators": True,
            "inserted_at": None,
            "updated_at": None,
        }

    def test_create_terms_metadata_without_options(self):
        property = rg.TermsMetadataProperty(name="metadata")

        assert property.title == "metadata"
        assert property.name == "metadata"
        assert property.visible_for_annotators is True
        assert property.options is None

        model = property.api_model()
        assert model.type == "terms"
        assert model.model_dump() == {
            "id": None,
            "dataset_id": None,
            "name": "metadata",
            "title": "metadata",
            "settings": {"type": "terms", "values": None, "visible_for_annotators": True},
            "type": "terms",
            "visible_for_annotators": True,
            "inserted_at": None,
            "updated_at": None,
        }

    def test_create_from_model(self):
        model = MetadataFieldModel(
            id=uuid.uuid4(),
            name="metadata",
            title="A metadata property",
            type="terms",
            settings=TermsMetadataPropertySettings(values=["option1", "option2"], type="terms"),
            visible_for_annotators=True,
        )

        property = rg.TermsMetadataProperty.from_model(model)

        assert property.id == model.id
        assert property.title == "A metadata property"
        assert property.name == "metadata"
        assert property.visible_for_annotators is True
        assert property.options == ["option1", "option2"]

    def test_create_integer_metadata_with_visible_for_annotators(self):
        metadata = rg.IntegerMetadataProperty(name="integer", min=10, visible_for_annotators=False)
        assert metadata.visible_for_annotators is False

    def test_create_float_metadata_with_visible_for_annotators(self):
        metadata = rg.FloatMetadataProperty(name="integer", min=3.5, max=10.5, visible_for_annotators=False)
        assert metadata.visible_for_annotators is False
