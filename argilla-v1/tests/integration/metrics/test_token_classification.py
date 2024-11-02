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
from argilla_v1.client.api import load, log
from argilla_v1.client.models import TokenClassificationRecord
from argilla_v1.metrics import entity_consistency
from argilla_v1.metrics.token_classification import (
    Annotations,
    entity_capitalness,
    entity_density,
    entity_labels,
    f1,
    mention_length,
    token_capitalness,
    token_frequency,
    token_length,
    tokens_length,
    top_k_mentions,
)

from tests.integration.utils import delete_ignoring_errors


def log_some_data(dataset: str):
    delete_ignoring_errors(dataset)
    text = "My first great example \n"
    tokens = text.split(" ")
    log(
        [
            TokenClassificationRecord(
                id=1,
                text=text,
                tokens=tokens,
                prediction=[("CARDINAL", 3, 8)],
                annotation=[("CARDINAL", 3, 8)],
            ),
            TokenClassificationRecord(
                id=2,
                text=text,
                tokens=tokens,
                prediction=[("CARDINAL", 3, 8)],
                annotation=[("CARDINAL", 3, 8)],
            ),
            TokenClassificationRecord(
                id=3,
                text=text,
                tokens=tokens,
                prediction=[("NUMBER", 3, 8)],
                annotation=[("NUMBER", 3, 8)],
            ),
            TokenClassificationRecord(
                id=4,
                text=text,
                tokens=tokens,
                prediction=[("PERSON", 3, 8)],
                annotation=[("PERSON", 3, 8)],
            ),
        ],
        name=dataset,
    )


def test_search_by_nested_metric(mocked_client):
    dataset = "test_search_by_nested_metric"
    delete_ignoring_errors(dataset)
    log_some_data(dataset)

    df = load(dataset, query="metrics.predicted.mentions.capitalness: LOWER")
    assert len(df) > 0


def test_tokens_length(mocked_client):
    dataset = "test_tokens_length"
    log_some_data(dataset)

    results = tokens_length(dataset)
    assert results
    assert results.data == {}
    results.visualize()


def test_token_length(mocked_client):
    dataset = "test_token_length"
    log_some_data(dataset)

    results = token_length(dataset)
    assert results
    assert results.data == {}
    results.visualize()


def test_token_frequency(mocked_client):
    dataset = "test_token_frequency"
    log_some_data(dataset)

    results = token_frequency(dataset)
    assert results
    assert results.data == {"\n": 4, "My": 4, "example": 4, "first": 4, "great": 4}
    results.visualize()


def test_token_capitalness(mocked_client):
    dataset = "test_token_capitalness"
    log_some_data(dataset)

    results = token_capitalness(dataset)
    assert results
    assert results.data == {"LOWER": 12, "FIRST": 4}
    results.visualize()


def test_mentions_length(mocked_client):
    dataset = "test_mentions_length"
    log_some_data(dataset)

    results = mention_length(dataset)
    assert results
    assert results.data == {}
    results.visualize()


def test_compute_for_as_string(mocked_client):
    dataset = "test_compute_for_as_string"
    log_some_data(dataset)

    results = entity_capitalness(dataset, compute_for="Predictions")
    assert results
    assert results.data == {"LOWER": 4}
    results.visualize()

    with pytest.raises(
        ValueError,
        match="not-found is not a valid ComputeFor, please select one of \['annotations', 'predictions'\]",
    ):
        entity_capitalness(dataset, compute_for="not-found")


def test_entity_density(mocked_client):
    dataset = "test_entity_density"
    log_some_data(dataset)

    results = entity_density(dataset)
    assert results
    assert results.data == {}
    results.visualize()


def test_entity_labels(mocked_client):
    dataset = "test_entity_labels"

    log_some_data(dataset)

    results = entity_labels(dataset)
    assert results
    assert results.data == {"CARDINAL": 2, "NUMBER": 1, "PERSON": 1}
    results.visualize()

    results = entity_labels(dataset, compute_for=Annotations)
    assert results
    assert results.data == {"CARDINAL": 2, "NUMBER": 1, "PERSON": 1}
    results.visualize()


def test_entity_capitalness(mocked_client):
    dataset = "test_entity_capitalness"
    delete_ignoring_errors(dataset)
    log_some_data(dataset)

    results = entity_capitalness(dataset)
    assert results
    assert results.data == {"LOWER": 4}
    results.visualize()

    results = entity_capitalness(dataset, compute_for=Annotations)
    assert results
    assert results.data == {"LOWER": 4}
    results.visualize()


def test_top_k_mentions_consistency(mocked_client):
    dataset = "test_top_k_mentions_consistency"
    delete_ignoring_errors(dataset)
    log_some_data(dataset)

    mentions = {
        "mentions": [
            {
                "mention": "first",
                "entities": [
                    {"count": 2, "label": "CARDINAL"},
                    {"count": 1, "label": "NUMBER"},
                    {"count": 1, "label": "PERSON"},
                ],
            }
        ]
    }
    filtered_mentions = {
        "mentions": [
            {
                "mention": "first",
                "entities": [
                    {"count": 1, "label": "NUMBER"},
                ],
            }
        ]
    }
    validate_mentions(
        dataset=dataset,
        expected_mentions=mentions,
    )

    validate_mentions(
        dataset=dataset,
        compute_for=Annotations,
        threshold=2,
        expected_mentions=mentions,
    )

    validate_mentions(
        dataset=dataset,
        post_label_filter={"NUMBER"},
        expected_mentions=filtered_mentions,
    )


def validate_mentions(
    *,
    dataset: str,
    expected_mentions: dict,
    **metric_args,
):
    results = top_k_mentions(dataset, **metric_args)
    assert results
    assert results.data == expected_mentions
    results.visualize()


@pytest.mark.parametrize(
    ("metric", "expected_results"),
    [
        (top_k_mentions, {"mentions": []}),
        (entity_consistency, {}),
        (mention_length, {}),
        (entity_density, {}),
        (entity_capitalness, {}),
        (entity_labels, {}),
    ],
)
def test_metrics_without_data(mocked_client, metric, expected_results, monkeypatch):
    dataset = "test_metrics_without_data"
    delete_ignoring_errors(dataset)

    text = "M"
    tokens = text.split(" ")
    log(
        TokenClassificationRecord(
            id=1,
            text=text,
            tokens=tokens,
        ),
        name=dataset,
    )

    results = metric(dataset)
    assert results
    assert results.data == expected_results
    results.visualize()


def test_metrics_for_token_classification(mocked_client):
    dataset = "test_metrics_for_token_classification"

    text = "test the f1 metric of the token classification task"
    log(
        TokenClassificationRecord(
            id=1,
            text=text,
            tokens=text.split(),
            prediction=[("a", 0, 4), ("b", 5, 8), ("b", 9, 11)],
            annotation=[("a", 0, 4), ("b", 5, 8), ("a", 9, 11)],
        ),
        name=dataset,
    )

    results = f1(dataset)
    assert results
    assert results.data == {
        "f1_macro": pytest.approx(0.75),
        "f1_micro": pytest.approx(0.6666666666666666),
        "a_f1": pytest.approx(0.6666666666666666),
        "a_precision": pytest.approx(1.0),
        "a_recall": pytest.approx(0.5),
        "b_f1": pytest.approx(0.6666666666666666),
        "b_precision": pytest.approx(0.5),
        "b_recall": pytest.approx(1.0),
        "precision_macro": pytest.approx(0.75),
        "precision_micro": pytest.approx(0.6666666666666666),
        "recall_macro": pytest.approx(0.75),
        "recall_micro": pytest.approx(0.6666666666666666),
    }
    results.visualize()
