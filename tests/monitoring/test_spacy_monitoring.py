import random

import rubrix as rb
from tests.monitoring.helpers import mock_monitor


def test_spacy_ner_monitor(monkeypatch, mocked_client):
    dataset = "spacy-dataset"
    rb.delete(dataset)

    import spacy

    nlp = spacy.load("en_core_web_sm")
    nlp = rb.monitor(nlp, dataset=dataset, sample_rate=0.5)
    mock_monitor(nlp, monkeypatch)

    random.seed(42)

    for _ in range(0, 20):
        nlp("Paris is my favourite city")

    df = rb.load(dataset)
    df = df.to_pandas()
    assert len(df) == 11
    # assert 10 - std < len(df) < 10 + std
    assert df.text.unique().tolist() == ["Paris is my favourite city"]

    rb.delete(dataset)
    list(nlp.pipe(["This is a text"] * 20))

    df = rb.load(dataset)
    df = df.to_pandas()
    assert len(df) == 6
    assert df.text.unique().tolist() == ["This is a text"]

    rb.delete(dataset)
    list(nlp.pipe([("This is a text", {"meta": "data"})] * 20, as_tuples=True))

    df = rb.load(dataset)
    assert len(df) == 14
    for metadata in df.metadata.values.tolist():
        assert metadata == {"meta": "data"}
