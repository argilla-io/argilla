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
from typing import Union
from unittest.mock import MagicMock

import pytest
from fastapi import Request
from starlette.responses import JSONResponse

from argilla_server.api.errors.v1.exception_handlers import set_request_error
from argilla_server.errors import ServerError
from argilla_server.models import (
    Record,
    User,
)
from argilla_server.telemetry import TelemetryClient
from tests.factories import (
    DatasetFactory,
    IntegerMetadataPropertyFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    SpanQuestionFactory,
    SuggestionFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
    VectorSettingsFactory,
    WorkspaceFactory,
)

mock_request = Request(scope={"type": "http", "headers": {}})

__CRUD__ = ["create", "read", "update", "delete"]


@pytest.mark.asyncio
class TestSuiteTelemetry:
    async def test_disable_telemetry(self):
        telemetry_client = TelemetryClient(enable_telemetry=False)

        assert telemetry_client.enable_telemetry == False

    async def test_track_endpoint(self, test_telemetry: TelemetryClient):
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
        await test_telemetry.track_endpoint(endpoint_path="/api/test/endpoint", request=request, response=response)

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

    async def test_track_endpoint_call_with_error(self, test_telemetry: TelemetryClient):
        request = Request(
            scope={
                "type": "http",
                "path": "/api/test/endpoint",
                "headers": {},
                "method": "POST",
            }
        )
        response = JSONResponse(content={"test": "test"}, status_code=500)
        await test_telemetry.track_endpoint(endpoint_path="/api/test/endpoint", request=request, response=response)

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

    async def test_track_endpoint_call_with_error_and_exception(self, test_telemetry: TelemetryClient):
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

        await test_telemetry.track_endpoint(endpoint_path="/api/test/endpoint", request=request, response=response)

        test_telemetry.track_data.assert_called_once_with(
            topic="endpoints",
            data={
                "endpoint": "POST /api/test/endpoint",
                "request.method": "POST",
                "request.user-agent": None,
                "request.accept-language": None,
                "response.status": "500",
                "response.error": "argilla.api.errors::ServerError()",
                "response.error_code": "argilla.api.errors::ServerError",
            },
        )

    async def test_track_user_login(self, test_telemetry: MagicMock):
        user = User(id=uuid.uuid4(), username="argilla")
        await test_telemetry.track_user_login(request=mock_request, user=user)
        test_telemetry.track_data.assert_called()

    @pytest.mark.parametrize("is_oauth", [True, False])
    async def test_track_crud_user(self, test_telemetry: MagicMock, is_oauth: bool):
        user = await UserFactory.create()
        await test_telemetry.track_crud_user(action="create", user=user, is_oauth=is_oauth)
        test_telemetry.track_data.assert_called()

    async def test_track_track_crud_workspace(self, test_telemetry: MagicMock):
        workspace = await WorkspaceFactory.create()
        await test_telemetry.track_crud_workspace(action="create", workspace=workspace)
        test_telemetry.track_data.assert_called()

    async def test_track_track_crud_dataset(
        self,
        test_telemetry: MagicMock,
    ):
        dataset = await DatasetFactory.create()
        await test_telemetry.track_crud_dataset(action="create", dataset=dataset)
        test_telemetry.track_data.assert_called()

    @pytest.mark.parametrize("record_or_dataset_factory", [RecordFactory, DatasetFactory])
    async def test_track_track_crud_records(
        self, test_telemetry: MagicMock, record_or_dataset_factory: Union[DatasetFactory, RecordFactory]
    ):
        record_or_dataset = await record_or_dataset_factory.create()
        if isinstance(record_or_dataset, Record):
            await ResponseFactory.create(record=record_or_dataset)
            await SuggestionFactory.create(record=record_or_dataset)
        await test_telemetry.track_crud_records(action="create", record_or_dataset=record_or_dataset)
        test_telemetry.track_data.assert_called()

    @pytest.mark.parametrize("action", __CRUD__)
    @pytest.mark.parametrize(
        "setting_factory_config",
        [
            ("vectors_settings", VectorSettingsFactory),
            ("metadata_properties", IntegerMetadataPropertyFactory),
            ("fields", TextFieldFactory),
            ("questions", RankingQuestionFactory),
            ("questions", RatingQuestionFactory),
            ("questions", LabelSelectionQuestionFactory),
            ("questions", MultiLabelSelectionQuestionFactory),
            ("questions", SpanQuestionFactory),
            ("questions", TextQuestionFactory),
        ],
    )
    async def test_track_crud_dataset_setting(self, test_telemetry: MagicMock, action: str, setting_factory_config):
        setting_name, setting_factory = setting_factory_config
        setting = await setting_factory.create_batch(size=1)
        setting_config = {setting_name: setting}
        dataset = await DatasetFactory.create(**setting_config)
        await test_telemetry.track_crud_dataset(action=action, dataset=dataset)
        test_telemetry.track_crud_dataset_setting.assert_called_with(
            action=action, setting_name=setting_name, setting=setting[0], dataset=dataset
        )
        test_telemetry.track_data.assert_called()
