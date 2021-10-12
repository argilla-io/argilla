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
import socket
from datetime import datetime

import pytest

from rubrix.client.models import TokenClassificationRecord
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    EntitySpan,
    TokenClassificationAnnotation,
    TokenClassificationBulkData,
    TokenClassificationQuery,
)
from rubrix.client.sdk.token_classification.models import (
    TokenClassificationRecord as SdkTokenClassificationRecord,
)
from rubrix.server.tasks.token_classification.api.model import (
    TokenClassificationBulkData as ServerTokenClassificationBulkData,
)
from rubrix.server.tasks.token_classification.api.model import (
    TokenClassificationQuery as ServerTokenClassificationQuery,
)


def test_bulk_data_schema(helpers):
    client_schema = TokenClassificationBulkData.schema()
    server_schema = ServerTokenClassificationBulkData.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )


def test_query_schema(helpers):
    client_schema = TokenClassificationQuery.schema()
    server_schema = ServerTokenClassificationQuery.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )


@pytest.mark.parametrize(
    "prediction,expected", [([("label", 0, 4)], 1.0), ([("label", 0, 4, 0.5)], 0.5)]
)
def test_from_client_prediction(prediction, expected):
    record = TokenClassificationRecord(
        text="this is a test text",
        tokens=["this", "is", "a", "test", "text"],
        prediction=prediction,
    )
    sdk_record = CreationTokenClassificationRecord.from_client(record)

    assert sdk_record.prediction.entities[0].score == pytest.approx(expected)


@pytest.mark.parametrize(
    "agent,expected", [(None, socket.gethostname()), ("agent", "agent")]
)
def test_from_client_agent(agent, expected):
    record = TokenClassificationRecord(
        text="this is a test text",
        tokens=["this", "is", "a", "test", "text"],
        prediction=[("label", 0, 4)],
        annotation=[("label", 0, 4)],
        prediction_agent=agent,
        annotation_agent=agent,
    )
    sdk_record = CreationTokenClassificationRecord.from_client(record)

    assert sdk_record.prediction.agent == expected
    assert sdk_record.annotation.agent == expected


def test_to_client():
    prediction = TokenClassificationAnnotation(
        entities=[EntitySpan(label="label1", start=0, end=4)], agent="agent"
    )

    sdk_record = SdkTokenClassificationRecord(
        raw_text="this is a test text",
        tokens=["this", "is", "a", "test", "text"],
        annotation=prediction,
        prediction=prediction,
        event_timestamp=datetime(2000, 1, 1),
    )

    record = sdk_record.to_client()

    assert isinstance(record, TokenClassificationRecord)
    assert record.prediction == [("label1", 0, 4, 1.0)]
    assert record.prediction_agent == "agent"
    assert record.annotation == [("label1", 0, 4)]
    assert record.annotation_agent == "agent"
