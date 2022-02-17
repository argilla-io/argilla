import rubrix as rb
from tests.monitoring.helpers import mock_monitor


def test_spacy_ner_monitor(monkeypatch, mocked_client):
    dataset = "spacy-dataset"
    rb.delete(dataset)

    import spacy

    nlp = spacy.load("en_core_web_sm")
    nlp = rb.monitor(nlp, dataset=dataset, sample_rate=0.1)
    mock_monitor(nlp, monkeypatch)

    for _ in range(0, 100):
        nlp("Paris is my favourite city")

    df = rb.load(dataset)
    assert 1 < len(df) <= 20
    assert df.text.unique().tolist() == ["Paris is my favourite city"]

    rb.delete(dataset)
    list(nlp.pipe(["This is a text"] * 100))

    df = rb.load(dataset)
    assert 1 < len(df) <= 20
    assert df.text.unique().tolist() == ["This is a text"]

    rb.delete(dataset)
    list(nlp.pipe([("This is a text", {"meta": "data"})] * 100, as_tuples=True))

    df = rb.load(dataset)
    assert 1 < len(df) <= 20
    for metadata in df.metadata.values.tolist():
        assert metadata == {"meta": "data"}
