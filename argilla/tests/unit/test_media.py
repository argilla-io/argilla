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
from PIL import Image
from argilla.media import pil_to_data_uri


def test_pil_to_data_uri_with_valid_image():
    image = Image.new("RGB", (100, 100), color="red")
    data_uri = pil_to_data_uri(image)
    assert isinstance(data_uri, str)
    assert data_uri.startswith("data:image/png;base64,")


def test_pil_to_data_uri_with_invalid_image():
    image = "not an image"
    with pytest.raises(ValueError):
        pil_to_data_uri(image)
