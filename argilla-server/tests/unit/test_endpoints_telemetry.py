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
from starlette.testclient import TestClient

from argilla_server._app import create_server_app
from argilla_server.settings import settings
from argilla_server.telemetry import TelemetryClient


class TestEndpointsTelemetry:
    def test_track_endpoint_call(self, test_telemetry: TelemetryClient):
        settings.enable_telemetry = True  # Forcing telemetry to be enabled for this test

        client = TestClient(create_server_app())

        client.get("/api/v1/version")

        test_telemetry.track_endpoint.assert_called_once_with("/api/v1/version", ANY, ANY)

    def test_track_endpoint_error_call(self, test_telemetry: TelemetryClient):
        settings.enable_telemetry = True

        client = TestClient(create_server_app())

        response = client.post("/api/v1/datasets")
        assert response.status_code == 401

        test_telemetry.track_endpoint.assert_called_once_with("/api/v1/datasets", ANY, ANY)

    def test_not_track_endpoint_call_with_disabled_telemetry(self, test_telemetry: TelemetryClient):
        settings.enable_telemetry = False

        client = TestClient(create_server_app())

        client.get("/api/v1/version")

        test_telemetry.track_endpoint.assert_not_called()
