import httpx
import pytest

import rubrix
import rubrix as rb
from rubrix.metrics.token_classification import (
    tokens_length,
    mention_length,
    entity_density,
    entity_capitalness,
    entity_consistency,
    entity_labels,
)
from tests.server.test_helpers import client


def mocking_client(monkeypatch):
    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "delete", client.delete)
    monkeypatch.setattr(httpx, "put", client.put)
    monkeypatch.setattr(httpx, "stream", client.stream)


def log_some_data(dataset: str):
    text = "My first rubrix example"
    tokens = text.split(" ")
    rubrix.delete(dataset)
    rb.log(
        [
            rb.TokenClassificationRecord(
                id=1,
                text=text,
                tokens=tokens,
                prediction=[("CARDINAL", 3, 8)],
            ),
            rb.TokenClassificationRecord(
                id=2,
                text=text,
                tokens=tokens,
                prediction=[("CARDINAL", 3, 8)],
            ),
            rb.TokenClassificationRecord(
                id=3,
                text=text,
                tokens=tokens,
                prediction=[("NUMBER", 3, 8)],
            ),
            rb.TokenClassificationRecord(
                id=4,
                text=text,
                tokens=tokens,
                prediction=[("PERSON", 3, 8)],
            ),
        ],
        name=dataset,
    )


def test_search_by_nested_metric(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_search_by_nested_metric"
    rb.delete(dataset)
    log_some_data(dataset)

    df = rb.load(dataset, query="metrics.mentions.predicted.capitalness: LOWER")
    assert len(df) > 0


def test_tokens_length(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_tokens_length"
    log_some_data(dataset)

    results = tokens_length(dataset)
    assert results
    assert results.data == {"4.0": 4}
    results.visualize()


def test_mentions_length(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_mentions_length"
    log_some_data(dataset)

    results = mention_length(dataset)
    assert results
    assert results.data == {"1.0": 4}
    results.visualize()


def test_entity_density(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_entity_density"
    log_some_data(dataset)

    results = entity_density(dataset)
    assert results
    assert results.data == {"0.25": 4}
    results.visualize()


def test_entity_labels(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_entity_labels"
    log_some_data(dataset)

    results = entity_labels(dataset)
    assert results
    assert results.data == {"CARDINAL": 2, "NUMBER": 1, "PERSON": 1}
    results.visualize()


def test_entity_capitalness(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_entity_capitalness"
    rubrix.delete(dataset)
    log_some_data(dataset)

    results = entity_capitalness(dataset)
    assert results
    assert results.data == {"LOWER": 4}
    results.visualize()


def test_entity_consistency(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_entity_consistency"
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
                ]
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
def test_metrics_without_data(metric, expected_results, monkeypatch):
    mocking_client(monkeypatch)
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
