#  coding=utf-8
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
import pytest
from httpx import Response as HttpxResponse

from rubrix.client.sdk.commons.api import build_bulk_response, build_data_response
from rubrix.client.sdk.commons.models import (
    BulkResponse,
    ErrorMessage,
    HTTPValidationError,
    Response,
    ValidationError,
)
from rubrix.client.sdk.text_classification.models import TextClassificationRecord


@pytest.mark.parametrize(
    "status_code, expected",
    [
        (200, BulkResponse),
        (404, ErrorMessage),
        (500, ErrorMessage),
        (422, HTTPValidationError),
    ],
)
def test_build_bulk_response(status_code, expected):
    server_response = None
    if status_code == 200:
        server_response = BulkResponse(dataset="test", failed=0, processed=0)
    elif status_code == 404:
        server_response = ErrorMessage(detail="test")
    elif status_code == 500:
        server_response = ErrorMessage(detail="test")
    elif status_code == 422:
        server_response = HTTPValidationError(
            detail=[ValidationError(loc=["test"], msg="test", type="test")]
        )

    httpx_response = HttpxResponse(
        status_code=status_code, content=server_response.json()
    )
    response = build_bulk_response(httpx_response)

    assert isinstance(response, Response)
    assert isinstance(response.parsed, expected)


@pytest.mark.parametrize(
    "status_code, expected",
    [
        (200, TextClassificationRecord),
        (404, ErrorMessage),
        (500, ErrorMessage),
        (422, HTTPValidationError),
    ],
)
def test_build_data_response(status_code, expected):
    server_response = None
    if status_code == 200:
        server_response = TextClassificationRecord(inputs={"text": "test"})
    elif status_code == 404:
        server_response = ErrorMessage(detail="test")
    elif status_code == 500:
        server_response = ErrorMessage(detail="test")
    elif status_code == 422:
        server_response = HTTPValidationError(
            detail=[ValidationError(loc=["test"], msg="test", type="test")]
        )

    httpx_response = HttpxResponse(
        status_code=status_code,
        content=server_response.json() + "\n" + server_response.json(),
    )
    response = build_data_response(httpx_response, data_type=TextClassificationRecord)

    assert isinstance(response, Response)
    if status_code == 200:
        assert isinstance(response.parsed, list) and len(response.parsed) == 2
        assert isinstance(response.parsed[0], expected)
    else:
        assert isinstance(response.parsed, expected)
