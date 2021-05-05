import pytest
from pydantic import ValidationError
from rubrix.server.tasks.token_classification.api.model import (
    EntitySpan,
    TokenClassificationAnnotation,
    TokenClassificationRecord,
)


def test_char_position():

    with pytest.raises(
        ValidationError,
        match="End character cannot be placed before the starting character,"
        " it must be at least one character after.",
    ):
        EntitySpan(start=1, end=1, label="label")

    text = "I am Maxi"
    TokenClassificationRecord(
        text=text,
        tokens=text.split(),
        prediction=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=0, end=1, label="test"),
                EntitySpan(start=2, end=len(text), label="test"),
            ],
        ),
    )


def test_fix_substrings():
    text = "On one ones o no"
    TokenClassificationRecord(
        text=text,
        tokens=text.split(),
        prediction=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=3, end=6, label="test"),
            ],
        ),
    )

def test_entities_with_spaces():

    text = "This is  a  great  space"
    TokenClassificationRecord(
        text=text,
        tokens=["This", "is", " ", "a", " ", "great", " ", "space"],
        prediction=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=9, end=len(text), label="test"),
            ],
        ),
    )