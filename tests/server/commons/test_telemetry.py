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
from argilla.server.commons.models import TaskType
from argilla.server.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    GenericServerError,
    ServerError,
)
from argilla.server.schemas.datasets import Dataset
from argilla.utils import telemetry
from argilla.utils.telemetry import TelemetryClient, get_telemetry_client
from fastapi import Request

mock_request = Request(scope={"type": "http", "headers": {}})


def test_disable_telemetry():
    telemetry_client = TelemetryClient(enable_telemetry=False)

    assert telemetry_client.client is None


@pytest.mark.asyncio
async def test_track_login(test_telemetry: MagicMock):
    await telemetry.track_login(request=mock_request, username="argilla")

    current_server_id = get_telemetry_client().server_id
    expected_event_data = {
        "accept-language": None,
        "is_default_user": True,
        "user-agent": None,
        "user_hash": str(uuid.uuid5(current_server_id, name="argilla")),
    }
    test_telemetry.assert_called_once_with("UserInfoRequested", expected_event_data)


@pytest.mark.asyncio
async def test_track_bulk(test_telemetry):
    task, records = TaskType.token_classification, 100

    await telemetry.track_bulk(task=task, records=records)
    test_telemetry.assert_called_once_with("LogRecordsRequested", {"task": task, "records": records})


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
async def test_track_error(test_telemetry, error, expected_event):
    await telemetry.track_error(error, request=mock_request)

    test_telemetry.assert_called_once_with("ServerErrorFound", expected_event)
