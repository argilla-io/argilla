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

from typing import TYPE_CHECKING
import io
import base64

if TYPE_CHECKING:
    from PIL import Image


def pil_to_data_uri(image_object: "Image") -> str:
    """Convert a PIL image to a base64 data URI string.
    Parameters:
        image_object (Image): The PIL image to convert to a base64 data URI.
    Returns:
        str: The data URI string.
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise ImportError("The PIL library is required to convert PIL images for upload.") from e

    if not isinstance(image_object, Image.Image):
        raise ValueError("The image_object must be a PIL Image object.")

    try:
        buffered = io.BytesIO()
        image_object.save(buffered, format=image_object.format)
    except Exception as e:
        raise ValueError("An error occurred while saving the image binary to buffer") from e

    try:
        img_str = base64.b64encode(buffered.getvalue()).decode()
        mimetype = f"image/{image_object.format.lower()}"
        data_uri = f"data:{mimetype};base64,{img_str}"
    except Exception as e:
        raise ValueError("An error occurred while converting the image binary to base64") from e

    return data_uri
