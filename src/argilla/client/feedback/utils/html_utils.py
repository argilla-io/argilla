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


import base64
import warnings
from pathlib import Path
from typing import Callable, List, Optional, Union

from argilla.utils.dependency import require_dependencies

# Define html supported types for each media
SUPPORTED_MEDIA_TYPES = {
    "video": ["mp4", "webm", "ogg"],
    "audio": ["mp3", "wav", "ogg"],
    "image": ["png", "jpg", "jpeg", "ico", "svg", "gif", "apng", "avif", "webp"],
}


def media_to_html(media_type: str, media_source: Union[str, bytes], file_type: Optional[str] = None) -> str:
    """
    Convert a media file to an HTML tag with embedded base64 data.

    Args:
        media_type: The type of media to convert. Can be one of 'video', 'audio', or 'image'.
        media_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the media file. If not provided, it will be inferred from the file extension.

    Returns:
        HTML tag with embedded base64 data.

    Raises:
        FileNotFoundError: If the file does not exist or is empty.
        ValueError: If no provided file type using bytes as input or the file type is not supported.
    """

    if isinstance(media_source, bytes):
        if not file_type:
            raise ValueError("File type must be provided if media source is a byte string.")

        file_data = media_source

    else:
        file_path = Path(media_source)

        if not file_path.exists() or file_path.stat().st_size == 0:
            raise FileNotFoundError(f"File {file_path} does not exist or is empty.")

        if not file_type:
            file_type = file_path.suffix[1:].lower()

        file_data = file_path.read_bytes()

    if len(file_data) > 5000000:
        raise ValueError(
            f"File size is {len(file_data)} bytes. It is recommended to use files smaller than 5MB, as larger files might not render properly."
        )

    if file_type not in SUPPORTED_MEDIA_TYPES[media_type]:
        raise ValueError(
            f"Unsupported {media_type} type: {file_type}. Supported types are {SUPPORTED_MEDIA_TYPES[media_type]}"
        )

    if file_type == "ogg":
        warnings.warn("'ogg' files might not be supported in Safari.", category=UserWarning)

    media_base64 = base64.b64encode(file_data).decode("utf-8")

    data_url = f"data:{media_type}/{file_type};base64,{media_base64}"

    if media_type == "video":
        html = f"<video controls><source src='{data_url}' type='video/{file_type}'></video>"
    elif media_type == "audio":
        html = f"<audio controls><source src='{data_url}' type='audio/{file_type}'></audio>"
    elif media_type == "image":
        html = f'<img src="{data_url}">'
    else:
        raise ValueError(f"Unsupported media type: {media_type}")  # Technically unreachable

    return html


def video_to_html(media_source: Union[str, bytes], file_type: Optional[str] = None) -> str:
    """
    Convert a video file to an HTML tag with embedded base64 data.

    Args:
        media_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the video file. If not provided, it will be inferred from the file extension.

    Returns:
        The HTML tag with embedded base64 data.

    Examples:
        >>> from argilla.client.feedback.utils import video_to_html
        >>> html = video_to_html("my_video.mp4")
    """
    return media_to_html("video", media_source, file_type)


def audio_to_html(media_source: Union[str, bytes], file_type: Optional[str] = None) -> str:
    """
    Convert an audio file to an HTML tag with embedded base64 data.

    Args:
        media_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the audio file. If not provided, it will be inferred from the file extension.

    Returns:
        The HTML tag with embedded base64 data.

    Examples:
        >>> from argilla.client.feedback.utils import audio_to_html
        >>> html = audio_to_html("my_audio.mp3")
    """
    return media_to_html("audio", media_source, file_type)


def image_to_html(media_source: Union[str, bytes], file_type: Optional[str] = None) -> str:
    """
    Convert an image file to an HTML tag with embedded base64 data.

    Args:
        media_source: The path to the media file or a non-b64 encoded byte string.
        file_type: The type of the image file. If not provided, it will be inferred from the file extension.

    Returns:
        The HTML tag with embedded base64 data.

    Examples:
        >>> from argilla.client.feedback.utils import image_to_html
        >>> html = image_to_html("my_image.png")
    """
    return media_to_html("image", media_source, file_type)


def create_token_highlights(
    tokens: List[str], weights: List[float], c_map: Optional[Union[str, Callable]] = "viridis"
) -> str:
    """
    Generates an HTML string with tokens highlighted based on the corresponding weights using a color map.

    Args:
        tokens: List of tokens to highlight.
        weights: List of weights corresponding to each token.
        c_map: Optional color map to use for highlighting. Can be a string (name of a matplotlib colormap)
                    or a callable that returns an RGB tuple

    Returns:
        An HTML string with the tokens highlighted.

    Raises:
        ValueError: If the length of tokens and weights is not the same.
        ValueError: If tokens or weights are empty.
        TypeError: If c_map is not a string or a callable.

    Examples:
        >>> from argilla.client.feedback.utils import create_token_highlights
        >>> tokens = ["This", "is", "a", "test"]
        >>> weights = [0.1, 0.2, 0.3, 0.4]
        >>> html = create_token_highlights(tokens, weights)
        >>> html = create_token_highlights(tokens, weights, c_map='viridis')
        >>> html = create_token_highlights(tokens, weights, c_map=custom_RGB)
    """
    require_dependencies("matplotlib")
    import matplotlib.pyplot as plt
    from matplotlib.colors import rgb2hex

    if len(tokens) != len(weights):
        raise ValueError("Length of tokens and weights must be the same.")

    if not tokens or not weights:
        raise ValueError("Token or weight lists must not be empty.")

    max_weight = max(weights)
    min_weight = min(weights)
    normalized_weights = [
        (w - min_weight) / (max_weight - min_weight) if max_weight != min_weight else 0 for w in weights
    ]

    html_str = ["<p>"]
    for token, weight in zip(tokens, normalized_weights):
        if weight == 0:
            html_str.append(f"{token} ")
            continue

        rgba = None

        if callable(c_map):
            rgba = c_map(weight)

        elif isinstance(c_map, str):
            cmap = plt.get_cmap(c_map)
            rgba = cmap(weight)[:3]

        else:
            raise TypeError("c_map must be either a string or a function.")

        hex_color = rgb2hex(rgba)
        html_str.append(f'<span style="background-color: {hex_color}">{token}</span> ')

    html_str.append("</p>")
    return "".join(html_str)
