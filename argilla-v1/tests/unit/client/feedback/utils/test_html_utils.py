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
from unittest import mock

import pytest
from argilla_v1.client.feedback.utils import (
    audio_to_html,
    create_token_highlights,
    get_file_data,
    image_to_html,
    media_to_html,
    pdf_to_html,
    video_to_html,
)


@pytest.mark.parametrize(
    "file_source, file_type, media_type, file_exists, file_size, expected_output, expected_exception",
    [
        ("path/to/image.jpg", "jpg", "image", True, 1000, (b"sample_data", "jpg"), None),
        (b"image_data", "jpg", "image", None, None, (b"image_data", "jpg"), None),
        ("path/to/video.mp4", "mp4", "video", True, 2000, (b"sample_data", "mp4"), None),
        (b"video_data", None, "video", None, None, None, ValueError),
        ("path/to/nonexistent.jpg", "jpg", "image", False, 0, None, FileNotFoundError),
        ("path/to/large_file.mp4", "mp4", "video", True, 6_000_000, None, ValueError),
        ("path/to/wrong_extension.txt", "jpg", "image", True, 1000, None, ValueError),
    ],
)
@mock.patch("pathlib.Path.exists")
@mock.patch("pathlib.Path.stat")
@mock.patch("pathlib.Path.read_bytes")
def test_get_file_data(
    mock_read_bytes,
    mock_stat,
    mock_exists,
    file_source,
    file_type,
    media_type,
    file_exists,
    file_size,
    expected_output,
    expected_exception,
):
    if isinstance(file_source, str):
        mock_exists.return_value = file_exists
        mock_stat.return_value = mock.Mock(st_size=file_size)
        if expected_exception == ValueError and file_size > 5_000_000:
            mock_read_bytes.return_value = b"a" * file_size
        else:
            mock_read_bytes.return_value = b"sample_data"

    if expected_exception:
        with pytest.raises(expected_exception):
            get_file_data(file_source, file_type, media_type)
    else:
        assert get_file_data(file_source, file_type, media_type) == expected_output


@pytest.mark.parametrize(
    "media_type, file_source, file_type, width, height, autoplay, loop, is_valid_dim, file_data, expected_output, expected_exception",
    [
        (
            "image",
            "path/to/image.jpg",
            "jpeg",
            "300px",
            "200px",
            False,
            False,
            True,
            b"image_data",
            '<img src="data:image/jpeg;base64,aW1hZ2VfZGF0YQ==" width=300px height=200px>',
            None,
        ),
        (
            "video",
            b"video_data",
            "mp4",
            None,
            None,
            True,
            True,
            True,
            b"video_data",
            "<video controls autoplay loop><source src='data:video/mp4;base64,dmlkZW9fZGF0YQ==' type='video/mp4'></video>",
            None,
        ),
        ("audio", "path/to/audio.mp3", "mp3", "100%", "invalid", False, False, False, b"audio_data", None, ValueError),
        ("document", "path/to/doc.txt", "txt", None, None, False, False, True, b"doc_data", None, ValueError),
    ],
)
@mock.patch("argilla_v1.client.feedback.utils.html_utils.get_file_data")
@mock.patch("argilla_v1.client.feedback.utils.html_utils.is_valid_dimension")
def test_media_to_html(
    mock_is_valid_dimension,
    mock_get_file_data,
    media_type,
    file_source,
    file_type,
    width,
    height,
    autoplay,
    loop,
    is_valid_dim,
    file_data,
    expected_output,
    expected_exception,
):
    mock_is_valid_dimension.return_value = is_valid_dim
    mock_get_file_data.return_value = (file_data, file_type)

    if expected_exception:
        with pytest.raises(expected_exception):
            media_to_html(media_type, file_source, file_type, width, height, autoplay, loop)
    else:
        assert media_to_html(media_type, file_source, file_type, width, height, autoplay, loop) == expected_output


@pytest.mark.parametrize(
    "func, input_file, expected",
    [
        (video_to_html, "test.mp4", "<video controls><source src='data:video/mp4;base64,{}' type='video/mp4'></video>"),
        (
            audio_to_html,
            "test.mp3",
            "<audio controls><source src='data:audio/mp3;base64,{}' type='audio/mp3'></audio>",
        ),
        (image_to_html, "test.png", '<img src="data:image/png;base64,{}">'),
        (
            pdf_to_html,
            "test.pdf",
            '<object id="pdf" data="data:application/pdf;base64,{}" type="application/pdf" width="1000px" height="1000px"><p>Unable to display PDF.</p></object>',
        ),
        (
            pdf_to_html,
            "https://my_pdf.pdf",
            '<embed src="https://my_pdf.pdf" type="application/pdf" width="1000px" height="1000px"></embed>',
        ),
    ],
)
def test_wrappers(func, input_file, expected, tmp_path):
    if "https://" in input_file:
        encoded_data = input_file
        assert func(encoded_data) == expected.format(encoded_data)
    else:
        temp_file = tmp_path / input_file
        temp_file.write_bytes(b"dummy_data")
        encoded_data = base64.b64encode(b"dummy_data").decode("utf-8")
        expected_html = expected.format(encoded_data)
        assert func(str(temp_file)) == expected_html


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
