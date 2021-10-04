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

from rubrix.client.sdk.text_classification.models import TextClassificationBulkData
from rubrix.server.tasks.text_classification.api.model import (
    TextClassificationBulkData as ServerTextClassificationBulkData,
)


def test_bulk_data_schema(helpers):
    client_schema = TextClassificationBulkData.schema()
    server_schema = ServerTextClassificationBulkData.schema()

    # we do not care about the doc strings (aka descriptions in the schema)
    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )


def test_from_client():
    raise NotImplementedError


def test_to_client():
    raise NotImplementedError
