from rubrix.server.tasks.text2text import (
    Text2TextAnnotation,
    Text2TextPrediction,
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
            ]
        ),
    )

    assert record.prediction.sentences[0].score == 1.0
    assert record.prediction.sentences[1].score == 0.6
    assert record.prediction.sentences[2].score == 0.5
