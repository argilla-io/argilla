import httpx

import rubrix as rb
from rubrix.metrics.token_classification import (
    tokens_length,
    mention_length,
    entity_density,
    entity_capitalness,
    mention_consistency,
    entity_tags,
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
        ],
        name=dataset,
    )


def test_tokens_length(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_tokens_length"
    log_some_data(dataset)

    results = tokens_length(dataset)
    assert results
    assert results.data == {"4.0": 2}
    results.visualize()


def test_mentions_length(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_mentions_length"
    log_some_data(dataset)

    results = mention_length(dataset)
    assert results
    assert results.data == {"1.0": 2}
    results.visualize()


def test_entity_density(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_entity_density"
    log_some_data(dataset)

    results = entity_density(dataset)
    assert results
    assert results.data == {"0.25": 2}
    results.visualize()


def test_entity_tags(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_entity_tags"
    log_some_data(dataset)

    results = entity_tags(dataset)
    assert results
    assert results.data == {'CARDINAL': 2}
    results.visualize()


def test_entity_capitalness(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_entity_capitalness"
    log_some_data(dataset)

    results = entity_capitalness(dataset)
    assert results
    assert results.data == {"LOWER": 2}
    results.visualize()


def test_mention_consistency(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_mention_consistency"
    log_some_data(dataset)

    results = mention_consistency(dataset)
    assert results
    assert results.data == {
        "mentions": [
            {"entities": [{"count": 2, "entity": "CARDINAL"}], "mention": "first"}
        ]
    }
    results.visualize()
