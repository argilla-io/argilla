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

from rubrix.client.models import TextClassificationRecord, TokenAttributions
from rubrix.client.sdk.text_classification.models import (
    ClassPrediction,
    CreationTextClassificationRecord,
    TextClassificationAnnotation,
    TextClassificationBulkData,
    TextClassificationQuery,
)
from rubrix.client.sdk.text_classification.models import (
    TextClassificationRecord as SdkTextClassificationRecord,
)
from rubrix.server.tasks.text_classification.api.model import (
    TextClassificationBulkData as ServerTextClassificationBulkData,
)
from rubrix.server.tasks.text_classification.api.model import (
    TextClassificationQuery as ServerTextClassificationQuery,
)


def test_bulk_data_schema(helpers):
    client_schema = TextClassificationBulkData.schema()
    server_schema = ServerTextClassificationBulkData.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )


def test_query_schema(helpers):
    client_schema = TextClassificationQuery.schema()
    server_schema = ServerTextClassificationQuery.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )


def test_from_client_explanation():
    token_attributions = [
        TokenAttributions(token="test", attributions={"label1": 1.0, "label2": 2.0})
    ]
    record = TextClassificationRecord(
        inputs={"text": "test"},
        prediction=[("label1", 0.5), ("label2", 0.5)],
        annotation="label1",
        explanation={"text": token_attributions},
        event_timestamp=datetime(2000, 1, 1),
        id=1,
    )
    sdk_record = CreationTextClassificationRecord.from_client(record)

    assert sdk_record.explanation["text"] == token_attributions


@pytest.mark.parametrize(
    "annotation,expected", [("label1", 1), (["label1", "label2"], 2)]
)
def test_from_client_annotation(annotation, expected):
    record = TextClassificationRecord(
        inputs={"text": "test"},
        annotation=annotation,
        multi_label=True,
    )
    sdk_record = CreationTextClassificationRecord.from_client(record)

    assert len(sdk_record.annotation.labels) == expected


@pytest.mark.parametrize(
    "agent,expected", [(None, socket.gethostname()), ("agent", "agent")]
)
def test_from_client_agent(agent, expected):
    record = TextClassificationRecord(
        inputs="test",
        prediction=[("label1", 0.5), ("label2", 0.5)],
        annotation="label1",
        prediction_agent=agent,
        annotation_agent=agent,
    )
    sdk_record = CreationTextClassificationRecord.from_client(record)

    assert sdk_record.annotation.agent == expected
    assert sdk_record.prediction.agent == expected


@pytest.mark.parametrize(
    "multi_label,expected", [(False, "label1"), (True, ["label1"])]
)
def test_to_client(multi_label, expected):
    annotation = TextClassificationAnnotation(
        labels=[ClassPrediction(**{"class": "label1"})], agent="agent"
    )
    prediction = TextClassificationAnnotation(
        labels=[
            ClassPrediction(**{"class": "label1", "score": 0.5}),
            ClassPrediction(**{"class": "label2", "score": 0.5}),
        ],
        agent="agent",
    )

    sdk_record = SdkTextClassificationRecord(
        inputs={"text": "test"},
        annotation=annotation,
        prediction=prediction,
        multi_label=multi_label,
        event_timestamp=datetime(2000, 1, 1),
    )

    record = sdk_record.to_client()

    assert record.prediction == [("label1", 0.5), ("label2", 0.5)]
    assert record.prediction_agent == "agent"
    assert record.annotation_agent == "agent"
    assert record.annotation == expected
