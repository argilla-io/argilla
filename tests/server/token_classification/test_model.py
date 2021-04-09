import pytest
from pydantic import ValidationError
from rubrix.server.commons.models import TaskStatus
from rubrix.server.token_classification.model import (
    EntitySpan,
    TokenClassificationAnnotation,
    TokenClassificationRecord,
)

def test_char_position():

    with pytest.raises(ValidationError, match="End character cannot be placed before the starting character, it must be at least one character after."):
        EntitySpan(start=1, end=1, start_token=1, end_token=2, label="label")

def test_token_position():

    with pytest.raises(ValidationError, match="End token cannot be lower or equal than the start token."):
        EntitySpan(start=1, end=2, start_token=1, end_token=1, label="label")
