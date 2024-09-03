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
from unittest.mock import patch, mock_open
from uuid import UUID

import pytest
from pytest_mock import MockerFixture

from argilla_server.settings import settings
from argilla_server.telemetry import get_server_id


class TestTelemetryHelpers:
    def test_get_server_id_without_existing_file(self, mocker: MockerFixture):
        mocker.patch.object(os.path, "exists", return_value=False)

        with patch("builtins.open", mock_open()) as mock:
            server_id = get_server_id()
            another_server_id = get_server_id()

            assert server_id != another_server_id
            assert mock.call_count == 2
            mock.assert_called_with(os.path.join(settings.home_path, "server_id.dat"), "w")

    def test_get_server_id_with_existing_file(self, mocker: MockerFixture):
        mocker.patch.object(os.path, "exists", return_value=True)

        with patch("builtins.open", mock_open(read_data="00000000-0000-0000-0000-000000000000")) as mock:
            server_id = get_server_id()
            assert server_id == UUID(int=0)
