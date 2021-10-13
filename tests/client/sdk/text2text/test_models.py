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

from rubrix.client.models import Text2TextRecord
from rubrix.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextAnnotation,
    Text2TextBulkData,
    Text2TextPrediction,
    Text2TextQuery,
)
from rubrix.client.sdk.text2text.models import Text2TextRecord as SdkText2TextRecord
from rubrix.server.tasks.text2text.api.model import (
    Text2TextBulkData as ServerText2TextBulkData,
)
from rubrix.server.tasks.text2text.api.model import (
    Text2TextQuery as ServerText2TextQuery,
)


def test_bulk_data_schema(helpers):
    client_schema = Text2TextBulkData.schema()
    server_schema = ServerText2TextBulkData.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )


def test_query_schema(helpers):
    client_schema = Text2TextQuery.schema()
    server_schema = ServerText2TextQuery.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )


@pytest.mark.parametrize(
    "prediction,expected",
    [
        (["texto de prueba para text2text", "texto de test para text2text"], 1.0),
        ([("texto de prueba para text2text", 0.5)], 0.5),
    ],
)
def test_from_client_prediction(prediction, expected):
    record = Text2TextRecord(
        text="Test text for text2text",
        prediction=prediction,
        annotation="texto de prueba para text2text",
        id=1,
    )
    sdk_record = CreationText2TextRecord.from_client(record)

    assert len(sdk_record.prediction.sentences) == len(prediction)
    assert all(
        [sentence.score == expected for sentence in sdk_record.prediction.sentences]
    )


@pytest.mark.parametrize(
    "agent,expected", [(None, socket.gethostname()), ("agent", "agent")]
)
def test_from_client_agent(agent, expected):
    record = Text2TextRecord(
        text="test",
        prediction=["prueba"],
        annotation="prueba",
        prediction_agent=agent,
        annotation_agent=agent,
    )
    sdk_record = CreationText2TextRecord.from_client(record)

    assert sdk_record.annotation.agent == expected
    assert sdk_record.prediction.agent == expected


def test_to_client():
    prediction = Text2TextAnnotation(
        sentences=[
            Text2TextPrediction(text="prueba", score=0.5),
            Text2TextPrediction(text="prueba2", score=0.5),
        ],
        agent="agent",
    )

    sdk_record = SdkText2TextRecord(
        text="test",
        prediction=prediction,
        annotation=prediction,
        event_timestamp=datetime(2000, 1, 1),
    )

    record = sdk_record.to_client()

    assert record.prediction == [("prueba", 0.5), ("prueba2", 0.5)]
    assert record.prediction_agent == "agent"
    assert record.annotation == "prueba"
    assert record.annotation_agent == "agent"
