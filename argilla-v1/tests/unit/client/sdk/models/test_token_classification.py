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
from argilla_server.apis.v0.models.token_classification import (
    TokenClassificationBulkRequest as ServerTokenClassificationBulkData,
)
from argilla_server.apis.v0.models.token_classification import (
    TokenClassificationQuery as ServerTokenClassificationQuery,
)
from argilla_v1.client.models import TokenClassificationRecord
from argilla_v1.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    EntitySpan,
    TokenClassificationAnnotation,
    TokenClassificationBulkData,
    TokenClassificationQuery,
)
from argilla_v1.client.sdk.token_classification.models import TokenClassificationRecord as SdkTokenClassificationRecord


def test_bulk_data_schema(helpers):
    client_schema = TokenClassificationBulkData.schema()
    server_schema = ServerTokenClassificationBulkData.schema()

    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


def test_query_schema(helpers):
    client_schema = TokenClassificationQuery.schema()
    server_schema = ServerTokenClassificationQuery.schema()

    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


@pytest.mark.parametrize(
    "prediction,expected",
    [
        ([("label", 0, 4)], 0.0),
        ([("label", 0, 4, None)], 0.0),
        ([("label", 0, 4, 0.5)], 0.5),
    ],
)
def test_from_client_prediction(prediction, expected):
    record = TokenClassificationRecord(
        text="this is a test text",
        tokens=["this", "is", "a", "test", "text"],
        prediction=prediction,
        metrics={"not_passed_on": 0},
    )
    sdk_record = CreationTokenClassificationRecord.from_client(record)

    assert sdk_record.prediction.entities[0].score == pytest.approx(expected)
    assert sdk_record.metrics == {}


@pytest.mark.parametrize(
    "pred_agent,annot_agent,pred_expected,annot_expected",
    [
        (None, None, socket.gethostname(), socket.gethostname()),
        ("pred_agent", "annot_agent", "pred_agent", "annot_agent"),
    ],
)
def test_from_client_agent(pred_agent, annot_agent, pred_expected, annot_expected):
    record = TokenClassificationRecord(
        text="this is a test text",
        tokens=["this", "is", "a", "test", "text"],
        prediction=[("label", 0, 4)],
        annotation=[("label", 0, 4)],
        prediction_agent=pred_agent,
        annotation_agent=annot_agent,
    )
    sdk_record = CreationTokenClassificationRecord.from_client(record)

    assert sdk_record.prediction.agent == pred_expected
    assert sdk_record.annotation.agent == annot_expected


def test_to_client():
    prediction = TokenClassificationAnnotation(
        entities=[EntitySpan(label="pred_label", start=0, end=4)], agent="pred_agent"
    )
    annotation = TokenClassificationAnnotation(
        entities=[EntitySpan(label="annot_label", start=5, end=7)], agent="annot_agent"
    )

    sdk_record = SdkTokenClassificationRecord(
        text="this is a test text",
        tokens=["this", "is", "a", "test", "text"],
        annotation=annotation,
        prediction=prediction,
        event_timestamp=datetime(2000, 1, 1),
        metrics={"tokens_length": 42},
    )

    record = sdk_record.to_client()

    assert isinstance(record, TokenClassificationRecord)
    assert record.prediction == [("pred_label", 0, 4, 1.0)]
    assert record.prediction_agent == "pred_agent"
    assert record.annotation == [("annot_label", 5, 7)]
    assert record.annotation_agent == "annot_agent"
    assert record.metrics == {"tokens_length": 42}
