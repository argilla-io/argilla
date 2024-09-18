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
from fastapi import Request
from pytest_mock import MockerFixture
from starlette.responses import JSONResponse

from argilla_server.api.errors.v1.exception_handlers import set_request_error
from argilla_server.errors import ServerError
from argilla_server.integrations.huggingface.spaces import HUGGINGFACE_SETTINGS
from argilla_server.telemetry import TelemetryClient

mock_request = Request(scope={"type": "http", "headers": {}})


@pytest.mark.asyncio
class TestSuiteTelemetry:
    async def test_create_client_with_server_id(self, mocker: MockerFixture):
        mock_server_id = uuid.uuid4()
        mocker.patch("argilla_server.telemetry._client.get_server_id", return_value=mock_server_id)

        test_telemetry = TelemetryClient()

        assert "server_id" in test_telemetry._system_info
        assert test_telemetry._system_info["server_id"] == mock_server_id.urn

    def test_create_client_with_persistent_storage_enabled(self):
        HUGGINGFACE_SETTINGS.space_persistent_storage_enabled = True

        test_telemetry = TelemetryClient()

        assert "persistent_storage_enabled" in test_telemetry._system_info
        assert test_telemetry._system_info["persistent_storage_enabled"] is True

    def test_create_client_with_persistent_storage_disabled(self):
        HUGGINGFACE_SETTINGS.space_persistent_storage_enabled = False

        test_telemetry = TelemetryClient()

        assert "persistent_storage_enabled" in test_telemetry._system_info
        assert test_telemetry._system_info["persistent_storage_enabled"] is False

    def test_track_data(self, mocker: MockerFixture):
        from argilla_server._version import __version__ as version

        mock = mocker.patch("argilla_server.telemetry._client.send_telemetry")

        telemetry = TelemetryClient()
        telemetry.track_data("test_topic", {"test": "test"})

        mock.assert_called_once_with(
            topic="argilla/server/test_topic",
            library_name="argilla-server",
            library_version=version,
            user_agent={"test": "test", **telemetry._system_info},
        )

    async def test_track_api_request(self, test_telemetry: TelemetryClient, mocker: MockerFixture):
        mocker.patch(
            "argilla_server.telemetry._client.resolve_endpoint_path_for_request", return_value="/api/test/endpoint"
        )

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
        mocker.patch(
            "argilla_server.telemetry._client.resolve_endpoint_path_for_request", return_value="/api/test/endpoint"
        )

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
        mocker.patch(
            "argilla_server.telemetry._client.resolve_endpoint_path_for_request", return_value="/api/test/endpoint"
        )

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

    def test_track_server_startup(self, test_telemetry: TelemetryClient):
        test_telemetry.track_server_startup()
        test_telemetry.track_data.assert_called_once_with(topic="startup")
