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

from typing import Union
from unittest.mock import MagicMock

import pytest
from argilla_server.models import (
    Record,
)
from argilla_server.telemetry import TelemetryClient
from fastapi import Request

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
    VectorSettingsFactory,
)

mock_request = Request(scope={"type": "http", "headers": {}})

__CRUD__ = ["create"]


@pytest.mark.asyncio
class TestSuiteTelemetry:
    async def test_disable_telemetry(self):
        telemetry_client = TelemetryClient(enable_telemetry=False)

        assert telemetry_client.enable_telemetry == False

    async def test_track_track_crud_dataset(
        self,
        mock_telemetry_client: MagicMock,
    ):
        dataset = await DatasetFactory.create()
        await mock_telemetry_client.track_crud_dataset(action="create", dataset=dataset)
        mock_telemetry_client.track_data.assert_called()

    @pytest.mark.parametrize("record_or_dataset_factory", [RecordFactory, DatasetFactory])
    async def test_track_track_crud_records(
        self, mock_telemetry_client: MagicMock, record_or_dataset_factory: Union[DatasetFactory, RecordFactory]
    ):
        record_or_dataset = await record_or_dataset_factory.create()
        if isinstance(record_or_dataset, Record):
            await ResponseFactory.create(record=record_or_dataset)
            await SuggestionFactory.create(record=record_or_dataset)
        await mock_telemetry_client.track_crud_records(action="create", record_or_dataset=record_or_dataset)
        mock_telemetry_client.track_data.assert_called()

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
    async def test_track_crud_dataset_setting(
        self, mock_telemetry_client: MagicMock, action: str, setting_factory_config
    ):
        setting_name, setting_factory = setting_factory_config
        setting = await setting_factory.create_batch(size=1)
        setting_config = {setting_name: setting}
        dataset = await DatasetFactory.create(**setting_config)
        await mock_telemetry_client.track_crud_dataset(action=action, dataset=dataset)
        mock_telemetry_client.track_crud_dataset_setting.assert_called_with(
            action=action, setting_name=setting_name, setting=setting[0], dataset=dataset
        )
        mock_telemetry_client.track_data.assert_called()
