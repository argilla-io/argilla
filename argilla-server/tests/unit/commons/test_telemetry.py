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

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import Request, APIRouter
from fastapi.routing import APIRoute
from pytest_mock import mocker, MockerFixture
from starlette.responses import JSONResponse

from argilla_server.api.errors.v1.exception_handlers import set_request_error
from argilla_server.errors import ServerError
from argilla_server.telemetry import TelemetryClient

mock_request = Request(scope={"type": "http", "headers": {}})


@pytest.mark.asyncio
class TestSuiteTelemetry:
    async def test_track_api_request(self, test_telemetry: TelemetryClient, mocker: MockerFixture):
        mocker.patch("argilla_server.telemetry.resolve_endpoint_path_for_request", return_value="/api/test/endpoint")

        request = Request(
            scope={
                "type": "http",
                "path": "/api/test/endpoint",
                "headers": [
                    (b"accept-language", b"en-US"),
                    (b"user-agent", b"test"),
                ],
                "method": "GET",
            }
        )
        response = JSONResponse(content={"test": "test"}, status_code=201, headers={"Server-Timing": "total;dur=50"})
        await test_telemetry.track_api_request(request=request, response=response)

        test_telemetry.track_data.assert_called_once_with(
            topic="endpoints",
            data={
                "endpoint": "GET /api/test/endpoint",
                "request.method": "GET",
                "request.user-agent": "test",
                "request.accept-language": "en-US",
                "response.status": "201",
                "duration_in_milliseconds": "50",
            },
        )

    async def test_track_api_request_call_with_error(self, test_telemetry: TelemetryClient, mocker: MockerFixture):
        mocker.patch("argilla_server.telemetry.resolve_endpoint_path_for_request", return_value="/api/test/endpoint")

        request = Request(
            scope={
                "type": "http",
                "path": "/api/test/endpoint",
                "headers": {},
                "method": "POST",
            }
        )
        response = JSONResponse(content={"test": "test"}, status_code=500)
        await test_telemetry.track_api_request(request=request, response=response)

        test_telemetry.track_data.assert_called_once_with(
            topic="endpoints",
            data={
                "endpoint": "POST /api/test/endpoint",
                "request.method": "POST",
                "request.user-agent": None,
                "request.accept-language": None,
                "response.status": "500",
            },
        )

    async def test_track_api_request_call_with_error_and_exception(
        self, test_telemetry: TelemetryClient, mocker: MockerFixture
    ):
        mocker.patch("argilla_server.telemetry.resolve_endpoint_path_for_request", return_value="/api/test/endpoint")

        request = Request(
            scope={
                "type": "http",
                "path": "/api/test/endpoint",
                "headers": {},
                "method": "POST",
            }
        )
        response = JSONResponse(content={"test": "test"}, status_code=500)
        set_request_error(request, ServerError("Test exception"))

        await test_telemetry.track_api_request(request=request, response=response)

        test_telemetry.track_data.assert_called_once_with(
            topic="endpoints",
            data={
                "endpoint": "POST /api/test/endpoint",
                "request.method": "POST",
                "request.user-agent": None,
                "request.accept-language": None,
                "response.status": "500",
                "response.error_code": "argilla.api.errors::ServerError",
            },
        )
