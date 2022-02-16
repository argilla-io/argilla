import pytest

import rubrix
import rubrix as rb
from rubrix.metrics.token_classification import (
    Annotations,
    entity_capitalness,
    entity_consistency,
    entity_density,
    entity_labels,
    f1,
    mention_length,
    token_capitalness,
    token_frequency,
    token_length,
    tokens_length,
)


def log_some_data(dataset: str):
    rubrix.delete(dataset)
    text = "My first rubrix example"
    tokens = text.split(" ")
    rb.log(
        [
            rb.TokenClassificationRecord(
                id=1,
                text=text,
                tokens=tokens,
                prediction=[("CARDINAL", 3, 8)],
                annotation=[("CARDINAL", 3, 8)],
            ),
            rb.TokenClassificationRecord(
                id=2,
                text=text,
                tokens=tokens,
                prediction=[("CARDINAL", 3, 8)],
                annotation=[("CARDINAL", 3, 8)],
            ),
            rb.TokenClassificationRecord(
                id=3,
                text=text,
                tokens=tokens,
                prediction=[("NUMBER", 3, 8)],
                annotation=[("NUMBER", 3, 8)],
            ),
            rb.TokenClassificationRecord(
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
    rb.delete(dataset)
    log_some_data(dataset)

    df = rb.load(dataset, query="metrics.predicted.mentions.capitalness: LOWER")
    assert len(df) > 0


def test_tokens_length(mocked_client):
    dataset = "test_tokens_length"
    log_some_data(dataset)

    results = tokens_length(dataset)
    assert results
    assert results.data == {"4.0": 4}
    results.visualize()


def test_token_length(mocked_client):
    dataset = "test_token_length"
    log_some_data(dataset)

    results = token_length(dataset)
    assert results
    assert results.data == {"2.0": 4, "3.0": 0, "4.0": 0, "5.0": 4, "6.0": 4, "7.0": 4}
    results.visualize()


def test_token_frequency(mocked_client):
    dataset = "test_token_frequency"
    log_some_data(dataset)

    results = token_frequency(dataset)
    assert results
    assert results.data == {"My": 4, "example": 4, "first": 4, "rubrix": 4}
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
    assert results.data == {"1.0": 4}
    results.visualize()

    results = mention_length(dataset, level="char")
    assert results
    assert results.data == {"5.0": 4}
    results.visualize()

    results = mention_length(dataset, compute_for=Annotations)
    assert results
    assert results.data == {"1.0": 4}
    results.visualize()

    results = mention_length(dataset, compute_for=Annotations, level="char")
    assert results
    assert results.data == {"5.0": 4}
    results.visualize()


def test_compute_for_as_string(mocked_client):
    dataset = "test_compute_for_as_string"
    log_some_data(dataset)

    results = entity_density(dataset, compute_for="Predictions")
    assert results
    assert results.data == {"0.25": 4}
    results.visualize()

    with pytest.raises(
        ValueError,
        match="not-found is not a valid ComputeFor, please select one of \['annotations', 'predictions'\]",
    ):
        entity_density(dataset, compute_for="not-found")


def test_entity_density(mocked_client):
    dataset = "test_entity_density"
    log_some_data(dataset)

    results = entity_density(dataset)
    assert results
    assert results.data == {"0.25": 4}
    results.visualize()

    results = entity_density(dataset, compute_for=Annotations)
    assert results
    assert results.data == {"0.25": 4}
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
    rubrix.delete(dataset)
    log_some_data(dataset)

    results = entity_capitalness(dataset)
    assert results
    assert results.data == {"LOWER": 4}
    results.visualize()

    results = entity_capitalness(dataset, compute_for=Annotations)
    assert results
    assert results.data == {"LOWER": 4}
    results.visualize()


def test_entity_consistency(mocked_client):
    dataset = "test_entity_consistency"
    rubrix.delete(dataset)
    log_some_data(dataset)

    results = entity_consistency(dataset, threshold=2)
    assert results
    assert results.data == {
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
    results.visualize()

    results = entity_consistency(dataset, compute_for=Annotations, threshold=2)
    assert results
    assert results.data == {
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
    results.visualize()


@pytest.mark.parametrize(
    ("metric", "expected_results"),
    [
        (entity_consistency, {"mentions": []}),
        (mention_length, {}),
        (entity_density, {}),
        (entity_capitalness, {}),
        (entity_labels, {}),
    ],
)
def test_metrics_without_data(mocked_client, metric, expected_results, monkeypatch):
    dataset = "test_metrics_without_data"
    rb.delete(dataset)

    text = "M"
    tokens = text.split(" ")
    rb.log(
        rb.TokenClassificationRecord(
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


def test_metrics_for_text_classification(mocked_client):
    dataset = "test_metrics_for_token_classification"

    text = "test the f1 metric of the token classification task"
    rb.log(
        rb.TokenClassificationRecord(
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
