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
from argilla_server.apis.v0.models.text_classification import LabelingRule as ServerLabelingRule
from argilla_server.apis.v0.models.text_classification import (
    LabelingRuleMetricsSummary as ServerLabelingRuleMetricsSummary,
)
from argilla_server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest as ServerTextClassificationBulkData,
)
from argilla_server.apis.v0.models.text_classification import TextClassificationQuery as ServerTextClassificationQuery
from argilla_v1.client.models import TextClassificationRecord, TokenAttributions
from argilla_v1.client.sdk.text_classification.models import (
    ClassPrediction,
    CreationTextClassificationRecord,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationAnnotation,
    TextClassificationBulkData,
    TextClassificationQuery,
)
from argilla_v1.client.sdk.text_classification.models import TextClassificationRecord as SdkTextClassificationRecord


def test_bulk_data_schema(helpers):
    client_schema = TextClassificationBulkData.schema()
    server_schema = ServerTextClassificationBulkData.schema()

    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


def test_query_schema(helpers):
    client_schema = TextClassificationQuery.schema()
    server_schema = ServerTextClassificationQuery.schema()

    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


def test_labeling_rule_schema(helpers):
    client_schema = LabelingRule.schema()
    server_schema = ServerLabelingRule.schema()

    assert helpers.are_compatible_api_schemas(client_schema, server_schema)


def test_labeling_rule_metrics_schema(helpers):
    client_schema = LabelingRuleMetricsSummary.schema()
    server_schema = ServerLabelingRuleMetricsSummary.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(server_schema)


def test_from_client_explanation():
    token_attributions = [TokenAttributions(token="test", attributions={"label1": 1.0, "label2": 2.0})]
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


@pytest.mark.parametrize("annotation,expected", [("label1", 1), (["label1", "label2"], 2)])
def test_from_client_annotation(annotation, expected):
    record = TextClassificationRecord(
        inputs={"text": "test"},
        annotation=annotation,
        multi_label=True,
    )
    sdk_record = CreationTextClassificationRecord.from_client(record)

    assert len(sdk_record.annotation.labels) == expected


@pytest.mark.parametrize(
    "pred_agent,annot_agent,pred_expected,annot_expected",
    [
        (None, None, socket.gethostname(), socket.gethostname()),
        ("pred_agent", "annot_agent", "pred_agent", "annot_agent"),
    ],
)
def test_from_client_agent(pred_agent, annot_agent, pred_expected, annot_expected):
    record = TextClassificationRecord(
        text="test",
        prediction=[("label1", 0.5), ("label2", 0.5)],
        annotation="label1",
        prediction_agent=pred_agent,
        annotation_agent=annot_agent,
        metrics={"not_passed_on": 0},
    )
    sdk_record = CreationTextClassificationRecord.from_client(record)

    assert sdk_record.annotation.agent == annot_expected
    assert sdk_record.prediction.agent == pred_expected
    assert sdk_record.metrics == {}


@pytest.mark.parametrize("multi_label,expected", [(False, "annot_label"), (True, ["annot_label"])])
def test_to_client(multi_label, expected):
    annotation = TextClassificationAnnotation(labels=[ClassPrediction(**{"class": "annot_label"})], agent="annot_agent")
    prediction = TextClassificationAnnotation(
        labels=[
            ClassPrediction(**{"class": "label1", "score": 0.5}),
            ClassPrediction(**{"class": "label2", "score": 0.5}),
        ],
        agent="pred_agent",
    )

    sdk_record = SdkTextClassificationRecord(
        inputs={"text": "test"},
        annotation=annotation,
        prediction=prediction,
        multi_label=multi_label,
        event_timestamp=datetime(2000, 1, 1),
        metrics={"tokens_length": 42},
    )

    record = sdk_record.to_client()

    assert record.text == "test"
    assert record.prediction == [("label1", 0.5), ("label2", 0.5)]
    assert record.prediction_agent == "pred_agent"
    assert record.annotation_agent == "annot_agent"
    assert record.annotation == expected
    assert record.metrics == {"tokens_length": 42}
