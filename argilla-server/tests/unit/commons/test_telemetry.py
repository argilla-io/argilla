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
from argilla_server import telemetry
from argilla_server.commons.models import TaskType
from argilla_server.enums import UserRole
from argilla_server.models import User
from argilla_server.telemetry import TelemetryClient, get_telemetry_client
from fastapi import Request

mock_request = Request(scope={"type": "http", "headers": {}})


def test_disable_telemetry():
    telemetry_client = TelemetryClient(enable_telemetry=False)

    assert telemetry_client.client is None


@pytest.mark.asyncio
async def test_track_login(test_telemetry: MagicMock):
    user = User(id=uuid.uuid4(), username="argilla")
    await telemetry.track_login(request=mock_request, user=user)

    current_server_id = get_telemetry_client().server_id
    expected_event_data = {
        "accept-language": None,
        "is_default_user": True,
        "user_id": str(user.id),
        "user-agent": None,
        "user_hash": str(uuid.uuid5(current_server_id, name="argilla")),
    }
    test_telemetry.track_data.assert_called_once_with(action="UserInfoRequested", data=expected_event_data)


@pytest.mark.asyncio
async def test_track_bulk(test_telemetry):
    task, records = TaskType.token_classification, 100

    await telemetry.track_bulk(task=task, records=records)
    test_telemetry.track_data.assert_called_once_with(
        action="LogRecordsRequested", data={"task": task, "records": records}
    )


@pytest.mark.parametrize("is_oauth", [True, False])
@pytest.mark.parametrize("username", ["argilla", "john"])
def test_user_created(test_telemetry, username: str, is_oauth: bool):
    user = User(id=uuid.uuid4(), username=username, role=UserRole.owner)

    telemetry.track_user_created(user=user, is_oauth=is_oauth)
    test_telemetry.track_data.assert_called_once_with(
        action="UserCreated",
        data={
            "is_default_user": username == "argilla",
            "is_oauth": is_oauth,
            "role": user.role,
            "user_id": str(user.id),
        },
    )
