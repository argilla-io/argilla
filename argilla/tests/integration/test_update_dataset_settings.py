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

import pytest

from argilla import Dataset, Settings, TextField, LabelQuestion, Argilla, VectorField, FloatMetadataProperty


@pytest.fixture
def dataset():
    return Dataset(
        name=f"test_dataset_{uuid.uuid4().int}",
        settings=Settings(
            fields=[TextField(name="text", use_markdown=False)],
            questions=[LabelQuestion(name="label", labels=["a", "b", "c"])],
        ),
    ).create()


class TestUpdateDatasetSettings:
    def test_update_settings(self, client: Argilla, dataset: Dataset):
        settings = dataset.settings

        settings.fields.text.use_markdown = True
        dataset.settings.vectors.add(VectorField(name="vector", dimensions=10))
        dataset.settings.metadata.add(FloatMetadataProperty(name="metadata"))
        dataset.settings.update()

        dataset = client.datasets(dataset.name)
        settings = dataset.settings
        assert settings.fields["text"].use_markdown is True
        assert settings.vectors["vector"].dimensions == 10
        assert isinstance(settings.metadata.metadata, FloatMetadataProperty)

        settings.vectors["vector"].title = "A new title for vector"

        settings.update()
        dataset = client.datasets(dataset.name)
        assert dataset.settings.vectors["vector"].title == "A new title for vector"
