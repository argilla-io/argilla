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
from argilla_server.apis.v0.models.text2text import Text2TextBulkRequest as ServerText2TextBulkData
from argilla_server.apis.v0.models.text2text import Text2TextQuery as ServerText2TextQuery
from argilla_v1.client.models import Text2TextRecord
from argilla_v1.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextAnnotation,
    Text2TextBulkData,
    Text2TextPrediction,
    Text2TextQuery,
)
from argilla_v1.client.sdk.text2text.models import Text2TextRecord as SdkText2TextRecord


def test_bulk_data_schema(helpers):
    client_schema = Text2TextBulkData.schema()
    server_schema = ServerText2TextBulkData.schema()
    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


def test_query_schema(helpers):
    client_schema = Text2TextQuery.schema()
    server_schema = ServerText2TextQuery.schema()

    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


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
        metrics={"not_passed_on": 0},
    )
    sdk_record = CreationText2TextRecord.from_client(record)

    assert len(sdk_record.prediction.sentences) == len(prediction)
    assert all([sentence.score == expected for sentence in sdk_record.prediction.sentences])
    assert sdk_record.metrics == {}


@pytest.mark.parametrize(
    "pred_agent,annot_agent,pred_expected,annot_expected",
    [
        (None, None, socket.gethostname(), socket.gethostname()),
        ("pred_agent", "annot_agent", "pred_agent", "annot_agent"),
    ],
)
def test_from_client_agent(pred_agent, annot_agent, pred_expected, annot_expected):
    record = Text2TextRecord(
        text="test",
        prediction=["prueba"],
        annotation="prueba",
        prediction_agent=pred_agent,
        annotation_agent=annot_agent,
    )
    sdk_record = CreationText2TextRecord.from_client(record)

    assert sdk_record.annotation.agent == annot_expected
    assert sdk_record.prediction.agent == pred_expected


def test_to_client():
    prediction = Text2TextAnnotation(
        sentences=[
            Text2TextPrediction(text="pred_prueba", score=0.5),
            Text2TextPrediction(text="pred_prueba2", score=0.5),
        ],
        agent="pred_agent",
    )
    annotation = Text2TextAnnotation(
        sentences=[
            Text2TextPrediction(text="annot_prueba", score=0.5),
            Text2TextPrediction(text="annot_prueba2", score=0.5),
        ],
        agent="annot_agent",
    )

    sdk_record = SdkText2TextRecord(
        text="test",
        prediction=prediction,
        annotation=annotation,
        event_timestamp=datetime(2000, 1, 1),
        metrics={"tokens_length": 42},
    )

    record = sdk_record.to_client()

    assert record.prediction == [("pred_prueba", 0.5), ("pred_prueba2", 0.5)]
    assert record.prediction_agent == "pred_agent"
    assert record.annotation == "annot_prueba"
    assert record.annotation_agent == "annot_agent"
    assert record.metrics == {"tokens_length": 42}
