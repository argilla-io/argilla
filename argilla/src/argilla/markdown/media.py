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
import re
import warnings
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

# Define html supported types for each media
SUPPORTED_MEDIA_TYPES = {
    "video": ["mp4", "webm", "ogg"],
    "audio": ["mp3", "wav", "ogg"],
    "image": ["png", "jpg", "jpeg", "ico", "svg", "gif", "apng", "avif", "webp"],
    "document": ["pdf"],
}


def _validate_media_type(media_type: str, file_type: str) -> None:
    """
    Utility function to validate if the given file type is supported by the given media type.

    Args:
        media_type: Type of media ('video', 'audio', or 'image').
        file_type: The type of the media file.
    """
    if file_type not in SUPPORTED_MEDIA_TYPES[media_type]:
        warnings.warn(
            f"This {file_type} might not be supported. Supported types for {media_type} are {SUPPORTED_MEDIA_TYPES[media_type]}",
            category=UserWarning,
        )

    if file_type == "ogg":
        warnings.warn("'ogg' files might not be supported in Safari.", category=UserWarning)


def _get_file_data(
    file_source: Union[str, bytes], file_type: Optional[str] = None, media_type: Optional[str] = None
) -> bytes:
    """
    Utility function to check the input file and get the file data as bytes.

    Args:
        file_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the video file. If not provided, it will be inferred from the file extension.
        media_type: Type of media ('video', 'audio', or 'image').

    Returns:
        File data as bytes.

    Raises:
        FileNotFoundError: If the file does not exist or is empty.
        ValueError: If no provided file type using bytes as input, the file type does not match the expected extension or the file size is too large (>5MB).
    """
    if isinstance(file_source, bytes):
        if not file_type:
            raise ValueError("File type must be provided if file source is a byte string.")
        file_type != "pdf" and _validate_media_type(media_type, file_type)
        file_data = file_source
    else:
        file_path = Path(file_source)
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise FileNotFoundError(f"File {file_path} does not exist or is empty.")

        file_type = file_type or file_path.suffix[1:].lower()
        if file_path.suffix.lower() != f".{file_type}":
            raise ValueError(f"Provided file is not a {file_type.upper()}.")

        file_type != "pdf" and _validate_media_type(media_type, file_type)

        file_data = file_path.read_bytes()

    if len(file_data) > 5_000_000:
        raise ValueError(
            f"File size is {len(file_data)} bytes. It is recommended to use files smaller than 5MB, as larger files might not render properly."
        )

    return file_data, file_type


def _is_valid_dimension(dim: Optional[str]) -> bool:
    """
    Utility function to validate if the given dimension is a pixel or percentage value.

    Args:
        dim: The dimension string to validate (e.g., '300px', '50%').

    Returns:
        True if valid, False otherwise.
    """
    if dim is None:
        return True
    return bool(re.match(r"^\d+(px|%)$", dim))


def _media_to_html(
    media_type: str,
    file_source: Union[str, bytes],
    file_type: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    autoplay: Optional[bool] = False,
    loop: Optional[bool] = False,
) -> str:
    """
    Convert a media file to an HTML tag with embedded base64 data.

    Args:
        media_type: Type of media ('video', 'audio', or 'image').
        file_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the video file. If not provided, it will be inferred from the file extension.
        width: Display width in HTML. Defaults to None.
        height: Display height in HTML. Defaults to None.
        autoplay: True to autoplay media. Defaults to False.
        loop: True to loop media. Defaults to False.

    Returns:
        HTML tag with embedded base64 data.

    Raises:
        ValueError: If the width and height are not pixel or percentage.
    """
    if not (_is_valid_dimension(width) or _is_valid_dimension(height)):
        raise ValueError("Width and height must be valid pixel (e.g., '300px') or percentage (e.g., '50%') values.")

    file_data, file_type = _get_file_data(file_source, file_type, media_type)
    media_base64 = base64.b64encode(file_data).decode("utf-8")
    data_url = f"data:{media_type}/{file_type};base64,{media_base64}"

    common_attrs = f"{f' width={width}' if width else ''}{f' height={height}' if height else ''}"
    media_attrs = f"{' autoplay' if autoplay else ''}{' loop' if loop else ''}"

    if media_type == "video":
        return f"<video controls{common_attrs}{media_attrs}><source src='{data_url}' type='video/{file_type}'></video>"
    elif media_type == "audio":
        return f"<audio controls{media_attrs}><source src='{data_url}' type='audio/{file_type}'></audio>"
    elif media_type == "image":
        return f'<img src="{data_url}"{common_attrs}>'
    else:
        raise ValueError(f"Unsupported media type: {media_type}")


def video_to_html(
    file_source: Union[str, bytes],
    file_type: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    autoplay: bool = False,
    loop: bool = False,
) -> str:
    """
    Convert a video file to an HTML tag with embedded base64 data.

    Args:
        file_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the video file. If not provided, it will be inferred from the file extension.
        width: Display width in HTML. Defaults to None.
        height: Display height in HTML. Defaults to None.
        autoplay: True to autoplay media. Defaults to False.
        loop: True to loop media. Defaults to False.

    Returns:
        The HTML tag with embedded base64 data.

    Examples:
        ```python
        from argilla.markdown import video_to_html
        html = video_to_html("my_video.mp4", width="300px", height="300px", autoplay=True, loop=True)
        ```
    """
    return _media_to_html("video", file_source, file_type, width, height, autoplay, loop)


def audio_to_html(
    file_source: Union[str, bytes],
    file_type: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    autoplay: bool = False,
    loop: bool = False,
) -> str:
    """
    Convert an audio file to an HTML tag with embedded base64 data.

    Args:
        file_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the audio file. If not provided, it will be inferred from the file extension.
        width: Display width in HTML. Defaults to None.
        height: Display height in HTML. Defaults to None.
        autoplay: True to autoplay media. Defaults to False.
        loop: True to loop media. Defaults to False.

    Returns:
        The HTML tag with embedded base64 data.

    Examples:
        ```python
        from argilla.markdown import audio_to_html
        html = audio_to_html("my_audio.mp3", width="300px", height="300px", autoplay=True, loop=True)
        ```
    """
    return _media_to_html("audio", file_source, file_type, width, height, autoplay, loop)


def image_to_html(
    file_source: Union[str, bytes],
    file_type: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
) -> str:
    """
    Convert an image file to an HTML tag with embedded base64 data.

    Args:
        file_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the image file. If not provided, it will be inferred from the file extension.
        width: Display width in HTML. Defaults to None.
        height: Display height in HTML. Defaults to None.

    Returns:
        The HTML tag with embedded base64 data.

    Examples:
        ```python
        from argilla.markdown import image_to_html
        html = image_to_html("my_image.png", width="300px", height="300px")
        ```
    """
    return _media_to_html("image", file_source, file_type, width, height)


def pdf_to_html(
    file_source: Union[str, bytes], width: Optional[str] = "1000px", height: Optional[str] = "1000px"
) -> str:
    """
    Convert a pdf file to an HTML tag with embedded data.

    Args:
        file_source: The path to the PDF file, a bytes object with PDF data, or a URL.
        width: Display width in HTML. Defaults to "1000px".
        height: Display height in HTML. Defaults to "1000px".

    Returns:
        HTML string embedding the PDF.

    Raises:
        ValueError: If the width and height are not pixel or percentage.

    Examples:
        ```python
        from argilla.markdown import pdf_to_html
        html = pdf_to_html("my_pdf.pdf", width="300px", height="300px")
        ```
    """
    if not _is_valid_dimension(width) or not _is_valid_dimension(height):
        raise ValueError("Width and height must be valid pixel (e.g., '300px') or percentage (e.g., '50%') values.")

    if isinstance(file_source, str) and urlparse(file_source).scheme in ["http", "https"]:
        return f'<embed src="{file_source}" type="application/pdf" width="{width}" height="{height}"></embed>'

    file_data, _ = _get_file_data(file_source, "pdf")
    pdf_base64 = base64.b64encode(file_data).decode("utf-8")
    data_url = f"data:application/pdf;base64,{pdf_base64}"
    return f'<object id="pdf" data="{data_url}" type="application/pdf" width="{width}" height="{height}"></object>'
