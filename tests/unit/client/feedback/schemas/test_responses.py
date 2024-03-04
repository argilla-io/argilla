import pytest

from argilla.feedback import SpanValueSchema


def test_create_span_response_wrong_limits():
    with pytest.raises(ValueError, match="The end of the span must be greater than the start."):
        SpanValueSchema(start=10, end=8, label="test")
