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

import os
from unittest import mock
from unittest.mock import MagicMock, ANY

import pytest
from pytest_mock import MockerFixture
from starlette.testclient import TestClient

from argilla_server._app import create_server_app
from argilla_server.settings import settings
from argilla_server.telemetry import TelemetryClient


class TestAPITelemetry:
    def test_track_api_request_call(self, test_telemetry: TelemetryClient):
        settings.enable_telemetry = True  # Forcing telemetry to be enabled for this test

        client = TestClient(create_server_app())

        client.get("/api/v1/version")

        test_telemetry.track_api_request.assert_called_once()

    def test_track_api_request_call_on_error(self, test_telemetry: TelemetryClient):
        settings.enable_telemetry = True

        client = TestClient(create_server_app())

        response = client.post("/api/v1/datasets")
        assert response.status_code == 401

        test_telemetry.track_api_request.assert_called_once()

    def test_track_api_request_with_unexpected_telemetry_error(
        self, test_telemetry: TelemetryClient, mocker: "MockerFixture"
    ):
        with mocker.patch.object(test_telemetry, "track_api_request", side_effect=Exception("mocked error")):
            settings.enable_telemetry = True

            client = TestClient(create_server_app())

            response = client.get("/api/v1/version")

            test_telemetry.track_api_request.assert_called_once()
            assert response.status_code == 200

    def test_not_track_api_request_call_when_disabled_telemetry(self, test_telemetry: TelemetryClient):
        settings.enable_telemetry = False

        client = TestClient(create_server_app())

        client.get("/api/v1/version")

        test_telemetry.track_api_request.assert_not_called()
