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

import pytest
from argilla.client.feedback.utils import (
    audio_to_html,
    create_token_highlights,
    image_to_html,
    media_to_html,
    pdf_to_html,
    video_to_html,
)


@pytest.mark.parametrize(
    "media_type, source, file_type, expected",
    [
        (
            "audio",
            "test.mp3",
            None,
            "<audio controls><source src='data:audio/mp3;base64,{}' type='audio/mp3'></audio>",
        ),
        (
            "video",
            "test with space.mp4",
            None,
            "<video controls><source src='data:video/mp4;base64,{}' type='video/mp4'></video>",
        ),
        (
            "video",
            "test.mp4",
            "mp4",
            "<video controls><source src='data:video/mp4;base64,{}' type='video/mp4'></video>",
        ),
        ("video", "test.mp4", None, "<video controls><source src='data:video/mp4;base64,{}' type='video/mp4'></video>"),
        ("image", "test.png", None, '<img src="data:image/png;base64,{}">'),
        ("video", "test.MP4", None, "<video controls><source src='data:video/mp4;base64,{}' type='video/mp4'></video>"),
        ("video", "test.avi", None, "Unsupported video type"),
        ("audio", "test.aac", None, "Unsupported audio type"),
        ("image", "test.bmp", None, "Unsupported image type"),
        ("video", "non_existent.mp4", None, "non_existent.mp4 does not exist or is empty."),
        ("video", "empty.mp4", None, "empty.mp4 does not exist or is empty."),
        (
            "video",
            b"dummy_data",
            "mp4",
            "<video controls><source src='data:video/mp4;base64,{}' type='video/mp4'></video>",
        ),
        (
            "audio",
            b"dummy_data",
            "mp3",
            "<audio controls><source src='data:audio/mp3;base64,{}' type='audio/mp3'></audio>",
        ),
        ("video", b"dummy_data", "mp4", "It is recommended to use files smaller than 5MB,"),
    ],
)
def test_media_to_html(media_type, source, file_type, expected, tmp_path):
    if isinstance(source, bytes):
        media_source = source
        if "It is recommended" in expected:
            media_source = media_source * 5000000
    else:
        temp_file = tmp_path / source
        if "does not exist" not in expected:
            temp_file.write_bytes(b"dummy_data" if not source.endswith("empty.mp4") else b"")
        media_source = str(temp_file)

    encoded_data = base64.b64encode(b"dummy_data").decode("utf-8")

    if expected.startswith("<"):
        expected = expected.format(encoded_data)

    try:
        result = media_to_html(media_type, media_source, file_type)
        assert result == expected
    except (ValueError, FileNotFoundError) as e:
        assert expected in str(e)


@pytest.mark.parametrize(
    "func, path, expected",
    [
        (video_to_html, "test.mp4", "<video controls><source src='data:video/mp4;base64,{}' type='video/mp4'></video>"),
        (
            audio_to_html,
            "test.mp3",
            "<audio controls><source src='data:audio/mp3;base64,{}' type='audio/mp3'></audio>",
        ),
        (image_to_html, "test.png", '<img src="data:image/png;base64,{}">'),
    ],
)
def test_wrappers(func, path, expected, tmp_path):
    temp_file = tmp_path / path
    temp_file.write_bytes(b"dummy_data")
    encoded_data = base64.b64encode(b"dummy_data").decode("utf-8")
    expected_html = expected.format(encoded_data)

    assert func(str(temp_file)) == expected_html


@pytest.mark.parametrize(
    "input_file, expected",
    [
        (
            "test.pdf",
            '<object id="pdf" data="data:application/pdf;base64,{}" type="application/pdf" width="700" height="700"><p>Unable to display PDF file.</p></object>',
        ),
        (
            b"dummy_data",
            '<object id="pdf" data="data:application/pdf;base64,{}" type="application/pdf" width="700" height="700"><p>Unable to display PDF file.</p></object>',
        ),
        (
            "https://my_pdf.pdf",
            '<embed src="https://my_pdf.pdf" type="application/pdf" width="700px" height="700px"/></embed>',
        ),
        ("non_existent.pdf", "does not exist or is empty."),
        ("empty.pdf", "does not exist or is empty."),
        ("test.txt", "Provided file is not a PDF."),
        ("large.pdf", "It is recommended to use files smaller than 5MB"),
    ],
)
def test_pdf_to_html(input_file, expected, tmp_path):
    if isinstance(input_file, bytes):
        file_data = input_file
    elif "https://" in input_file:
        file_data = input_file
    elif "large.pdf" in input_file:
        temp_file = tmp_path / "large.pdf"
        temp_file.write_bytes(b"dummy_data" * 5000010)
        file_data = str(temp_file)
    else:
        temp_file = tmp_path / input_file
        if "non_existent.pdf" not in input_file and "empty.pdf" not in input_file:
            temp_file.write_bytes(b"dummy_data")
        file_data = str(temp_file)

    encoded_data = base64.b64encode(b"dummy_data").decode("utf-8")

    if expected.startswith("<"):
        expected = expected.format(encoded_data)

    try:
        result = pdf_to_html(file_data)
        assert result == expected
    except (ValueError, FileNotFoundError) as e:
        assert expected in str(e)


@pytest.mark.parametrize(
    "tokens,weights,c_map,expected_error,expected_substr",
    [
        (["token1", "token2"], [0.2], None, ValueError, None),
        (["token1", "token2"], [0.2, 0.8], 42, TypeError, None),
        (["token1", "token2"], [0.2, 0.8], lambda x: (1, 0, 0, 1), None, "#ff0000"),
        (["token1", "token2"], [0, 0], None, None, "<p>token1 token2 </p>"),
        ([], [], None, ValueError, None),
        (["token1"], [0.5], None, None, "token1"),
        (["token1", "token2"], [0.5, 0.8], "viridis", None, '<span style="background-color:'),
    ],
)
def test_create_token_highlights(tokens, weights, c_map, expected_error, expected_substr):
    if expected_error:
        with pytest.raises(expected_error):
            create_token_highlights(tokens, weights, c_map)
    else:
        result = create_token_highlights(tokens, weights, c_map)
        assert expected_substr in result
