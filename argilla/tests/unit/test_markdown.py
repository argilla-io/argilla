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

import pytest
from argilla.markdown import audio_to_html, chat_to_html, image_to_html, pdf_to_html, video_to_html
from argilla.markdown.media import _get_file_data, _is_valid_dimension, _media_to_html, _validate_media_type


def test_validate_media_type_valid():
    _validate_media_type("video", "mp4")
    _validate_media_type("audio", "mp3")
    _validate_media_type("image", "png")


def test_validate_media_type_invalid():
    with pytest.warns(UserWarning):
        _validate_media_type("video", "pdf")


def test_get_file_data_from_bytes():
    file_data = b"some data"
    result = _get_file_data(file_data, "mp4", "video")
    assert result[0] == file_data
    assert result[1] == "mp4"


def test_media_is_valid_dimension():
    # Test valid dimensions
    assert _is_valid_dimension("300px")
    assert _is_valid_dimension("50%")
    assert _is_valid_dimension(None)
    # Test invalid dimensions
    assert not _is_valid_dimension("300")
    assert not _is_valid_dimension("px")


def test_media_to_html():
    # Test media to HTML for video
    file_data = b"some video data"
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")
    expected_html = f"<video controls width=300px height=300px><source src='data:video/mp4;base64,{file_data_base64}' type='video/mp4'></video>"
    result = _media_to_html("video", file_data, "mp4", "300px", "300px")
    assert result == expected_html

    # Test media to HTML for audio
    file_data = b"some audio data"
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")
    expected_html = f"<audio controls><source src='data:audio/mp3;base64,{file_data_base64}' type='audio/mp3'></audio>"
    result = _media_to_html("audio", file_data, "mp3")
    assert result == expected_html

    # Test media to HTML for image
    file_data = b"some image data"
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")
    expected_html = f'<img src="data:image/png;base64,{file_data_base64}" width=300px height=300px>'
    result = _media_to_html("image", file_data, "png", "300px", "300px")
    assert result == expected_html


def test_video_to_html():
    file_data = b"some video data"
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")
    expected_html = f"<video controls width=300px height=300px><source src='data:video/mp4;base64,{file_data_base64}' type='video/mp4'></video>"
    result = video_to_html(file_data, "mp4", "300px", "300px")
    assert result == expected_html


def test_audio_to_html():
    file_data = b"some audio data"
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")
    expected_html = f"<audio controls><source src='data:audio/mp3;base64,{file_data_base64}' type='audio/mp3'></audio>"
    result = audio_to_html(file_data, "mp3")
    assert result == expected_html


def test_image_to_html():
    file_data = b"some image data"
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")
    expected_html = f'<img src="data:image/png;base64,{file_data_base64}" width=300px height=300px>'
    result = image_to_html(file_data, "png", "300px", "300px")
    assert result == expected_html


def test_pdf_to_html():
    file_data = b"%PDF-1.4 some pdf data"
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")
    expected_html = f'<object id="pdf" data="data:application/pdf;base64,{file_data_base64}" type="application/pdf" width="300px" height="300px"></object>'
    result = pdf_to_html(file_data, "300px", "300px")
    assert result == expected_html


def test_chat_to_html_multiple_messages():
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
        {"role": "system", "content": "system message"},
    ]
    expected_result = """<body>
    <style>
        .user-message, .system-message {
            display: flex;
            margin: 10px;
        }
        .user-message {
            justify-content: flex-end;
        }
        .system-message {
            justify-content: flex-start;
        }
        .user-message .message-content {
            background-color: #c2e3f7;
            color: #000000;
        }
        .system-message .message-content {
            background-color: #f5f5f5;
            color: #000000;
        }
        .message-content {
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
    </style>
    <div class="user-message"><div class="message-content"><p>hello</p></div></div><div class="system-message"><div class="message-content"><p>hi there</p></div></div><div class="system-message"><div class="message-content"><p>system message</p></div></div></body>"""
    result = chat_to_html(messages)
    assert result == expected_result


def test_chat_to_html_invalid_role():
    messages = [{"role": "unknown", "content": "hello"}]
    with pytest.raises(ValueError):
        chat_to_html(messages)
