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
from tempfile import NamedTemporaryFile

import pytest
from PIL import Image
from argilla._helpers._media import cast_image, pil_to_data_uri, uncast_image


@pytest.fixture
def pil_image():
    image = Image.new("RGB", (100, 100), color="red")
    return image


@pytest.fixture
def data_uri_image(pil_image):
    data_uri = pil_to_data_uri(pil_image)
    return data_uri


@pytest.fixture
def path_to_image(pil_image):
    with NamedTemporaryFile(suffix=".jpg") as f:
        pil_image.save(f.name)
        yield f.name


def test_cast_image_with_pil_image(pil_image):
    result = cast_image(pil_image)
    uncasted = uncast_image(result)

    assert isinstance(result, str)
    assert result.startswith("data:image")
    assert "base64" in result

    assert isinstance(uncasted, Image.Image)
    assert uncasted.size == pil_image.size
    assert uncasted.mode == pil_image.mode
    assert uncasted.getcolors() == pil_image.getcolors()


def test_cast_image_with_file_path(path_to_image):
    result = cast_image(path_to_image)
    uncasted = uncast_image(result)
    pil_image = Image.open(path_to_image)

    assert isinstance(result, str)
    assert result.startswith("data:image")
    assert "base64" in result

    assert isinstance(uncasted, Image.Image)
    assert uncasted.size == pil_image.size
    assert uncasted.mode == pil_image.mode
    assert uncasted.getcolors() == pil_image.getcolors()


def test_cast_image_with_data_uri(data_uri_image):
    result = cast_image(data_uri_image)
    uncasted = uncast_image(result)

    assert result == data_uri_image
    assert isinstance(uncasted, Image.Image)


def test_cast_image_with_invalid_input():
    invalid_input = 123
    with pytest.raises(ValueError):
        cast_image(invalid_input)


def test_uncast_image_with_url():
    image_url = "https://example.com/image.jpg"
    result = uncast_image(image_url)
    assert result == image_url
