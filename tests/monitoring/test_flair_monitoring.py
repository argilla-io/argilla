from tests.monitoring.helpers import mock_monitor


def test_flair_monitoring(mocked_client, monkeypatch):

    from flair.data import Sentence
    from flair.models import SequenceTagger

    import rubrix as rb

    dataset = "test_flair_monitoring"
    model = "flair/ner-english"

    rb.delete(dataset)

    # load tagger
    tagger = SequenceTagger.load(model)
    tagger = rb.monitor(
        tagger,
        dataset=dataset,
        sample_rate=1.0,
        agent=model,
    )

    mock_monitor(tagger, monkeypatch)
    # make example sentence
    expected_text = "George Washington went to Washington"
    sentence = Sentence(expected_text)
    # predict NER tags
    tagger.predict(sentence)

    detected_labels = sentence.get_labels("ner")
    records = rb.load(dataset, as_pandas=False)
    assert len(records) == 1

    record = records[0]
    assert record.text == expected_text
    assert record.tokens == [token.text for token in sentence.tokens]

    assert len(record.prediction) == len(detected_labels)
    for ((label, start, end, score), span) in zip(record.prediction, detected_labels):
        assert label == span.value
        assert start == span.span.start_pos
        assert end == span.span.end_pos
        assert score == span.score
