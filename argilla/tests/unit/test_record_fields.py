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

import pytest
import random
from tempfile import NamedTemporaryFile

from PIL import Image

from argilla import Record, Settings, ImageField, Dataset


@pytest.fixture
def pil_image():
    image = Image.new("RGB", (100, 100), color="red")
    return image


@pytest.fixture
def path_to_image(pil_image):
    with NamedTemporaryFile(suffix=".jpg") as f:
        pil_image.save(f.name)
        yield f.name


@pytest.fixture
def dataset():
    dataset = Dataset(
        name=f"test_dataset_{random.randint(1, 1000)}",
        settings=Settings(
            fields=[ImageField(name="image")],
        ),
    )
    return dataset


class TestRecordFields:
    def test_create_record_fields(self):
        record = Record(fields={"name": "John Doe"}, metadata={"age": 30})

        fields = record.fields
        assert fields["name"] == "John Doe"
        assert record.metadata["age"] == 30

    def test_create_record_image_path(self):
        record = Record(fields={"image": "path/to/image.jpg"})

        fields = record.fields
        assert fields["image"] == "path/to/image.jpg"

    def test_create_dataset_with_local_image(self, path_to_image, pil_image, dataset):
        record = Record(fields={"image": path_to_image}, _dataset=dataset)

        assert isinstance(record.fields["image"], Image.Image)
        assert record.fields["image"].size == pil_image.size
        assert record.fields["image"].mode == pil_image.mode

    def test_create_record_image_pil(self, pil_image, dataset):
        record = Record(fields={"image": pil_image}, _dataset=dataset)

        fields = record.fields
        assert isinstance(fields["image"], Image.Image)
        assert fields["image"].size == pil_image.size
        assert fields["image"].mode == pil_image.mode

    def test_create_record_with_wrong_image_type(self, dataset):
        record = Record(fields={"image": 123}, _dataset=dataset)
        with pytest.raises(ValueError):
            record.fields.to_dict()
        with pytest.raises(ValueError):
            record.fields["image"]
