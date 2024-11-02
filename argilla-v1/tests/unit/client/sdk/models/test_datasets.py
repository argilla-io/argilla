#  coding=utf-8
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
from argilla_server.schemas.v0.datasets import Dataset as ServerDataset
from argilla_v1.client.sdk.datasets.models import Dataset, TaskType


def test_dataset_schema(helpers):
    client_schema = Dataset.schema()
    server_schema = helpers.remove_key(ServerDataset.schema(), key="created_by")  # don't care about creator here

    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


def test_TaskType_enum():
    with pytest.raises(ValueError, match="mock is not a valid TaskType"):
        TaskType("mock")
