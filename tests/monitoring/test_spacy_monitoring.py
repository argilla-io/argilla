import rubrix as rb
from tests.monitoring.helpers import mock_monitor
from tests.server.test_helpers import client, mocking_client


def test_spacy_ner_monitor(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "spacy-dataset"
    rb.delete(dataset)

    import spacy

    nlp = spacy.load("en_core_web_sm")
    nlp = rb.monitor(nlp, dataset=dataset, sample_rate=0.5)
    mock_monitor(nlp, monkeypatch)

    for _ in range(0, 10):
        nlp("Paris is my favourite city")

    df = rb.load(dataset)
    assert 1 < len(df) <= 7
    assert df.text.unique().tolist() == ["Paris is my favourite city"]

    rb.delete(dataset)
    list(nlp.pipe(["This is a text"] * 10))

    df = rb.load(dataset)
    assert 1 < len(df) <= 7
    assert df.text.unique().tolist() == ["This is a text"]
