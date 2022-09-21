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

import pytest
from fastapi import Request

from rubrix.server.commons import telemetry
from rubrix.server.commons.models import TaskType
from rubrix.server.errors import RubrixServerError

mock_request = Request(scope={"type": "http", "headers": {}})


@pytest.mark.asyncio
async def test_track_login(telemetry_track_data):
    await telemetry.track_login(request=mock_request, username="rubrix")

    current_server_id = telemetry._TelemetryClient.get().server_id
    expected_event_data = {
        "accept-language": None,
        "is_default_user": True,
        "user-agent": None,
        "user_hash": str(uuid.uuid5(current_server_id, name="rubrix")),
    }
    telemetry_track_data.assert_called_once_with(
        "UserInfoRequested",
        expected_event_data,
    )


@pytest.mark.asyncio
async def test_track_bulk(telemetry_track_data):
    task, records = TaskType.token_classification, 100

    await telemetry.track_bulk(task=task, records=records)
    telemetry_track_data.assert_called_once_with(
        "LogRecordsRequested", {"task": task, "records": records}
    )


@pytest.mark.asyncio
async def test_track_error(telemetry_track_data):
    error = RubrixServerError()
    await telemetry.track_error(error, request=mock_request)
    telemetry_track_data.assert_called_once_with(
        "ServerErrorFound",
        {
            "accept-language": None,
            "code": "rubrix.api.errors::RubrixServerError",
            "user-agent": None,
        },
    )
