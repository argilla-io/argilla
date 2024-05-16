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
from argilla_server.errors import APIErrorHandler
from argilla_server.errors.base_errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    GenericServerError,
    ServerError,
)
from argilla_server.schemas.v0.datasets import Dataset
from fastapi import Request

mock_request = Request(scope={"type": "http", "headers": {}})


@pytest.mark.asyncio
class TestAPIErrorHandler:
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
    async def test_track_error(self, test_telemetry, error, expected_event):
        await APIErrorHandler.track_error(error, request=mock_request)

        test_telemetry.track_data.assert_called_once_with(action="ServerErrorFound", data=expected_event)
