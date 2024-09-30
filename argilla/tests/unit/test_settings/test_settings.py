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
import copy
import uuid

import pytest
from pytest_mock import MockerFixture

import argilla as rg
from argilla import Dataset
from argilla._exceptions import SettingsError
from argilla._models import DatasetModel
from argilla.settings._task_distribution import TaskDistribution


class TestSettings:
    def test_init_settings(self):
        settings = rg.Settings()
        assert len(settings.fields) == 0
        assert len(settings.questions) == 0

    def test_with_guidelines(self):
        mock_guidelines = "This is a guideline"
        settings = rg.Settings(
            guidelines=mock_guidelines,
        )
        assert settings.guidelines == mock_guidelines

    def test_with_guidelines_attribute(self):
        mock_guidelines = "This is a guideline"
        settings = rg.Settings()
        settings.guidelines = mock_guidelines
        assert settings.guidelines == mock_guidelines

    def test_with_text_field(self):
        mock_name = "prompt"
        mock_use_markdown = True
        settings = rg.Settings(fields=[rg.TextField(name=mock_name, use_markdown=mock_use_markdown)])
        assert settings.fields[0].name == mock_name
        assert settings.fields[0].use_markdown == mock_use_markdown

    def test_with_text_field_attribute(self):
        settings = rg.Settings()
        mock_name = "prompt"
        mock_use_markdown = True
        settings.fields = [rg.TextField(name=mock_name, use_markdown=mock_use_markdown)]
        assert settings.fields[0].name == mock_name
        assert settings.fields[0].use_markdown == mock_use_markdown

    def test_with_label_question(self):
        settings = rg.Settings(questions=[rg.LabelQuestion(name="sentiment", labels=["positive", "negative"])])
        assert settings.questions[0].name == "sentiment"
        assert settings.questions[0].labels == ["positive", "negative"]

    def test_with_label_question_attribute(self):
        settings = rg.Settings()
        settings.questions = [rg.LabelQuestion(name="sentiment", labels=["positive", "negative"])]
        assert settings.questions[0].name == "sentiment"
        assert settings.questions[0].labels == ["positive", "negative"]

    def test_settings_repr(self):
        settings = rg.Settings(
            fields=[
                rg.TextField(name="text", title="text"),
                rg.ImageField(name="image", title="image"),
            ],
            metadata=[
                rg.FloatMetadataProperty("source"),
            ],
            questions=[
                rg.LabelQuestion(name="label", title="text", labels=["positive", "negative"]),
                rg.RatingQuestion(name="rating", title="text", values=[1, 2, 3, 4, 5]),
                rg.TextQuestion(name="text", title="text"),
                rg.SpanQuestion(
                    name="span",
                    title="text",
                    field="text",
                    labels=["Apparatus", "Method", "Machine", "Manufacture", "Design"],
                    visible_labels=3,
                ),
            ],
            vectors=[rg.VectorField(name="text", dimensions=3)],
        )
        assert (
            settings.__repr__() == f"Settings(guidelines=None, allow_extra_metadata=False, "
            "distribution=OverlapTaskDistribution(min_submitted=1), "
            f"fields={settings.fields}, questions={settings.questions}, vectors={settings.vectors}, metadata={settings.metadata})"
        )

    def test_settings_validation_with_duplicated_names(self):
        settings = rg.Settings(
            fields=[rg.TextField(name="text", title="text")],
            metadata=[rg.FloatMetadataProperty("source")],
            questions=[rg.LabelQuestion(name="label", title="text", labels=["positive", "negative"])],
            vectors=[rg.VectorField(name="text", dimensions=3)],
        )

        with pytest.raises(SettingsError, match="names of dataset settings must be unique"):
            settings.validate()

    def test_copy_settings(self):
        settings = rg.Settings(
            fields=[rg.TextField(name="text", title="text")],
            metadata=[rg.FloatMetadataProperty("source")],
            questions=[rg.LabelQuestion(name="label", title="text", labels=["positive", "negative"])],
            vectors=[rg.VectorField(name="text", dimensions=3)],
        )

        settings_copy = copy.copy(settings)
        assert settings == settings_copy

        settings.fields["text"].title = "New title"
        assert settings == settings_copy

    def test_custom_copy_settings(self):
        settings = rg.Settings(
            fields=[rg.TextField(name="text", title="text")],
            metadata=[rg.FloatMetadataProperty("source")],
            questions=[rg.LabelQuestion(name="label", title="text", labels=["positive", "negative"])],
            vectors=[rg.VectorField(name="text", dimensions=3)],
        )

        settings_copy = settings._copy()
        assert settings == settings_copy

        settings.fields["text"].title = "New title"
        assert settings != settings_copy

    def test_settings_access(self):
        fields = [rg.TextField(name="text"), rg.TextField(name="other-text")]
        for field in fields:
            field._model.id = uuid.uuid4()

        settings = rg.Settings(fields=fields)

        assert settings.fields[0] == settings.fields["text"]
        assert settings.fields[1] == settings.fields["other-text"]
        assert settings.fields[fields[0].id] == fields[0]
        assert settings.fields[fields[1].id] == fields[1]

    def test_settings_access_by_none_id(self):
        settings = rg.Settings(fields=[rg.TextField(name="text", title="title")])
        assert settings.fields[None] is None

    def test_settings_access_by_missing(self):
        field = rg.TextField(name="text", title="title")
        field._model.id = uuid.uuid4()

        settings = rg.Settings(fields=[field])
        assert settings.fields[uuid.uuid4()] is None
        assert settings.fields["missing"] is None

    def test_settings_access_by_out_of_range(self):
        settings = rg.Settings(fields=[rg.TextField(name="text", title="title")])
        with pytest.raises(IndexError):
            _ = settings.fields[10]

    def test_settings_with_modified_default_task_distribution(self):
        settings = rg.Settings(fields=[rg.TextField(name="text", title="title")])

        assert settings.distribution == TaskDistribution(min_submitted=1)
        settings.distribution.min_submitted = 10

        other_settings = rg.Settings(fields=[rg.TextField(name="text", title="title")])
        assert other_settings.distribution == TaskDistribution(min_submitted=1)

    def test_read_settings_without_distribution(self, mocker: "MockerFixture"):
        settings = rg.Settings(
            fields=[rg.TextField(name="text", title="title")],
            _dataset=Dataset(name="dataset"),
        )

        mocker.patch.object(settings, "_fetch_fields", return_value=[f for f in settings.fields])
        mocker.patch.object(settings, "_fetch_questions", return_value=[])
        mocker.patch.object(settings, "_fetch_vectors", return_value=[])
        mocker.patch.object(settings, "_fetch_metadata", return_value=[])

        mocker.patch.object(
            settings._client.api.datasets,
            "get",
            return_value=DatasetModel(name=settings.dataset.name, distribution=None),
        )

        settings.get()
        assert settings.distribution == TaskDistribution.default()

    class TestSettingsSerialization:
        def test_serialize(self):
            settings = rg.Settings(
                guidelines="This is a guideline",
                fields=[rg.TextField(name="prompt", use_markdown=True)],
                questions=[rg.LabelQuestion(name="sentiment", labels=["positive", "negative"])],
            )
            settings_serialized = settings.serialize()
            assert settings_serialized["guidelines"] == "This is a guideline"
            assert settings_serialized["fields"][0]["name"] == "prompt"
            assert settings_serialized["fields"][0]["settings"]["use_markdown"] is True
