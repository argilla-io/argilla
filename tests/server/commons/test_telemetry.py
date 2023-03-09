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
from argilla.server.commons import telemetry
from argilla.server.commons.models import TaskType
from argilla.server.commons.telemetry import TelemetryClient
from argilla.server.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    GenericServerError,
    ServerError,
)
from argilla.server.schemas.datasets import Dataset
from fastapi import Request

mock_request = Request(scope={"type": "http", "headers": {}})


def test_disable_telemetry():
    telemetry_client = TelemetryClient(enable_telemetry=False)

    assert telemetry_client.client is None


@pytest.mark.asyncio
async def test_track_login(telemetry_track_data):
    await telemetry.track_login(request=mock_request, username="argilla")

    current_server_id = telemetry.telemetry_client.server_id
    expected_event_data = {
        "accept-language": None,
        "is_default_user": True,
        "user-agent": None,
        "user_hash": str(uuid.uuid5(current_server_id, name="argilla")),
    }
    telemetry_track_data.assert_called_once_with("UserInfoRequested", expected_event_data)


@pytest.mark.asyncio
async def test_track_bulk(telemetry_track_data):
    task, records = TaskType.token_classification, 100

    await telemetry.track_bulk(task=task, records=records)
    telemetry_track_data.assert_called_once_with("LogRecordsRequested", {"task": task, "records": records})


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["error", "expected_event"],
    [
        (
            EntityNotFoundError(name="mock-name", type="MockType"),
            {
                "accept-language": None,
                "code": "argilla.api.errors::EntityNotFoundError",
                "type": "MockType",
                "user-agent": None,
            },
        ),
        (
            EntityAlreadyExistsError(name="mock-name", type=Dataset, workspace="mock-workspace"),
            {
                "accept-language": None,
                "code": "argilla.api.errors::EntityAlreadyExistsError",
                "type": "Dataset",
                "user-agent": None,
            },
        ),
        (
            GenericServerError(RuntimeError("This is a mock error")),
            {
                "accept-language": None,
                "code": "argilla.api.errors::GenericServerError",
                "type": "builtins.RuntimeError",
                "user-agent": None,
            },
        ),
        (
            ServerError(),
            {
                "accept-language": None,
                "code": "argilla.api.errors::ServerError",
                "user-agent": None,
            },
        ),
    ],
)
async def test_track_error(telemetry_track_data, error, expected_event):
    await telemetry.track_error(error, request=mock_request)

    telemetry_track_data.assert_called_once_with("ServerErrorFound", expected_event)
