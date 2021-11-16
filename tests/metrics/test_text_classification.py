import httpx

from tests.server.test_helpers import client


def mocking_client(monkeypatch):
    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "delete", client.delete)
    monkeypatch.setattr(httpx, "put", client.put)
    monkeypatch.setattr(httpx, "stream", client.stream)


def test_metrics_for_text_classification(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_metrics_for_text_classification"

    import rubrix as rb

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                inputs={"text": "my first rubrix example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my first rubrix example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
            ),
        ],
        name=dataset,
    )

    from rubrix.metrics.text_classification import f1, f1_multilabel

    results = f1(dataset)
    assert results
    assert results.data == {
        "micro": 1.0,
        "macro": 1.0,
        "per_label": {"spam": 1.0, "ham": 1.0},
    }
    results.visualize()

    results = f1_multilabel(dataset)
    assert results
    assert results.data == {
        "micro": 1.0,
        "macro": 1.0,
        "per_label": {"spam": 1.0, "ham": 1.0},
    }
    results.visualize()


def test_f1_without_results(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_f1_without_results"
    import rubrix as rb

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                inputs={"text": "my first rubrix example"},
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my first rubrix example"},
            ),
        ],
        name=dataset,
    )

    from rubrix.metrics.text_classification import f1

    results = f1(dataset)
    assert results
    assert results.data == {}
    results.visualize()
