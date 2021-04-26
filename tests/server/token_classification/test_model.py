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
            agent="test", entities=[EntitySpan(start=0, end=1, label="test")]
        ),
    )
