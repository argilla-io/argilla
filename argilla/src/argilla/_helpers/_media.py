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

import base64
import io
import warnings
from pathlib import Path
from typing import Union

from PIL import Image


def pil_to_data_uri(image_object: "Image") -> str:
    """Convert a PIL image to a base64 data URI string.
    Parameters:
        image_object (Image): The PIL image to convert to a base64 data URI.
    Returns:
        str: The data URI string.
    """
    if not isinstance(image_object, Image.Image):
        raise ValueError("The image_object must be a PIL Image object.")

    image_format = image_object.format
    if image_format is None:
        image_format = "PNG"
        warnings.warn("The image format is not set. Defaulting to PNG.", UserWarning)

    try:
        buffered = io.BytesIO()
        image_object.save(buffered, format=image_format)
    except Exception as e:
        raise ValueError("An error occurred while saving the image binary to buffer") from e

    try:
        img_str = base64.b64encode(buffered.getvalue()).decode()
        mimetype = f"image/{image_format.lower()}"
        data_uri = f"data:{mimetype};base64,{img_str}"
    except Exception as e:
        raise ValueError("An error occurred while converting the image binary to base64") from e

    return data_uri


def filepath_to_data_uri(file_path: "Path") -> str:
    """Convert an image file to a base64 data URI string."""
    file_path = Path(file_path)
    if file_path.exists():
        with open(file_path, "rb") as image_file:
            img_str = base64.b64encode(image_file.read()).decode()
            mimetype = f"image/{file_path.suffix[1:]}"
            data_uri = f"data:{mimetype};base64,{img_str}"
    else:
        raise FileNotFoundError(f"File not found at {file_path}")

    return data_uri


def cast_image(image: Union["Image", str, Path]) -> str:
    """Convert a PIL image to a base64 data URI string.
    Parameters:
        image_object (Image): The PIL image to convert to a base64 data URI.
    Returns:
        str: The data URI string.
    """
    if isinstance(image, str):
        if image.startswith("data:") or image.startswith("http"):
            return image
        else:
            return filepath_to_data_uri(image)
    elif isinstance(image, Path):
        return filepath_to_data_uri(image)
    elif isinstance(image, Image.Image):
        return pil_to_data_uri(image)
    else:
        raise ValueError("The image must be a data URI string, a file path, or a PIL Image object.")


def uncast_image(image: str) -> "Image":
    """Convert a base64 data URI string to a PIL image."""
    if isinstance(image, Image.Image):
        return image
    elif not isinstance(image, str):
        raise ValueError("The image must be a data URI string.")
    elif image.startswith("data:image"):
        try:
            image_data = base64.b64decode(image.split(",")[1])
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise ValueError("An error occurred while converting the data URI to a PIL image.") from e
        return image
    elif image.startswith("http"):
        return image
    elif Path(image).exists():
        return Image.open(image)
    else:
        raise ValueError("The image must be a data URI string.")
