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

import numpy as np
import pytest

from argilla_v1.client.feedback.metrics.annotator_metrics import (
    F1ScoreMetric,
    PrecisionMetric,
    RecallMetric,
)

RESPONSES = ["positive", "negative", "positive", "negative", "positive", "negative", "positive", "positive", "negative"]
SUGGESTIONS = [
    "positive",
    "positive",
    "positive",
    "negative",
    "negative",
    "positive",
    "negative",
    "positive",
    "negative",
]

METRICS = [PrecisionMetric, RecallMetric, F1ScoreMetric]


@pytest.mark.parametrize("metric_cls", METRICS, ids=["precision", "recall", "f1-score"])
def test_binary_metrics_are_deterministic(metric_cls):
    # https://github.com/argilla-io/argilla/issues/5873: the binary branch of
    # these metrics used unseeded random.choice() to pick pos_label, so repeated
    # calls on identical inputs produced different scores.
    scores = {metric_cls()._compute(RESPONSES, SUGGESTIONS) for _ in range(20)}
    assert len(scores) == 1


@pytest.mark.parametrize("metric_cls", METRICS, ids=["precision", "recall", "f1-score"])
def test_binary_metrics_use_last_sorted_label_as_pos_label(metric_cls):
    from sklearn.metrics import f1_score, precision_score, recall_score

    sklearn_fn = {PrecisionMetric: precision_score, RecallMetric: recall_score, F1ScoreMetric: f1_score}[metric_cls]
    expected = sklearn_fn(RESPONSES, SUGGESTIONS, average="binary", pos_label=np.unique(RESPONSES)[-1])
    assert metric_cls()._compute(RESPONSES, SUGGESTIONS) == pytest.approx(expected)
