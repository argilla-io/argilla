from rubrix.server.tasks.text2text import (
    Text2TextAnnotation,
    Text2TextPrediction,
    Text2TextQuery,
    Text2TextRecord,
)


def test_sentences_sorted_by_score():

    record = Text2TextRecord(
        text="The inpu2 text",
        prediction=Text2TextAnnotation(
            agent="test_sentences_sorted_by_score",
            sentences=[
                Text2TextPrediction(text="sentence 1", score=0.6),
                Text2TextPrediction(text="sentence 2", score=0.5),
                Text2TextPrediction(text="sentence 3", score=1.0),
            ],
        ),
    )

    assert record.prediction.sentences[0].score == 1.0
    assert record.prediction.sentences[1].score == 0.6
    assert record.prediction.sentences[2].score == 0.5


def test_model_dict():
    record = Text2TextRecord(
        id=0,
        text="The input text",
        prediction=Text2TextAnnotation(
            agent="test_sentences_sorted_by_score",
            sentences=[
                Text2TextPrediction(text="sentence 1", score=0.6),
                Text2TextPrediction(text="sentence 2", score=0.5),
                Text2TextPrediction(text="sentence 3", score=1.0),
            ],
        ),
    )
    assert record.dict(exclude_none=True) == {
        "id": 0,
        "metrics": {},
        "prediction": {
            "agent": "test_sentences_sorted_by_score",
            "sentences": [
                {"score": 1.0, "text": "sentence 3"},
                {"score": 0.6, "text": "sentence 1"},
                {"score": 0.5, "text": "sentence 2"},
            ],
        },
        "status": "Default",
        "text": "The input text",
    }


def test_query_as_elasticsearch():
    query = Text2TextQuery(ids=[1, 2, 3])
    assert query.as_elasticsearch() == {"ids": {"values": query.ids}}
