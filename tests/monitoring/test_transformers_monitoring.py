import rubrix
from tests.monitoring.helpers import mock_monitor
from tests.server.test_helpers import client, mocking_client


def test_classifier_monitoring(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_classifier_monitoring"
    rubrix.delete(dataset)

    from transformers import pipeline

    sentiment_classifier = pipeline(
        model="distilbert-base-uncased-finetuned-sst-2-english",
        task="sentiment-analysis",
    )

    sentiment_classifier = rubrix.monitor(
        sentiment_classifier, dataset=dataset, sample_rate=1.0
    )

    mock_monitor(sentiment_classifier, monkeypatch)

    expected_text = "This is a text, yeah"
    sentiment_classifier(expected_text)

    df = rubrix.load(dataset)
    assert len(df) == 1
    assert df.inputs.values.tolist() == [{"text": expected_text}]

    rubrix.delete(dataset)
    texts = ["This is a text", "And another text here"]
    sentiment_classifier(texts)
    df = rubrix.load(dataset)
    assert len(df) == 2
    assert set([r["text"] for r in df.inputs.values.tolist()]) == set(texts)

    rubrix.delete(dataset)
    sentiment_classifier(expected_text, metadata={"some": "metadata"})
    df = rubrix.load(dataset)
    assert len(df) == 1
    assert df.metadata.values.tolist()[0] == {"some": "metadata"}
