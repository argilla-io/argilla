import pytest
from pydantic import ValidationError

from rubrix.client.models import TextClassificationRecord
from rubrix.client.models import TokenClassificationRecord


@pytest.mark.parametrize(
    ("annotation", "status", "expected_status"),
    [
        (None, None, "Default"),
        ("test", None, "Validated"),
        (None, "Discarded", "Discarded"),
        ("test", "Discarded", "Discarded"),
    ],
)
def test_text_classification_record(annotation, status, expected_status):
    """Just testing its dynamic defaults"""
    record = TextClassificationRecord(
        inputs={"text": "test"}, annotation=annotation, status=status
    )
    assert record.status == expected_status


@pytest.mark.parametrize(
    ("annotation", "status", "expected_status"),
    [
        (None, None, "Default"),
        ([("test", 0, 5)], None, "Validated"),
        (None, "Discarded", "Discarded"),
        ([("test", 0, 5)], "Discarded", "Discarded"),
    ],
)
def test_token_classification_record(annotation, status, expected_status):
    """Just testing its dynamic defaults"""
    record = TokenClassificationRecord(
        text="test text", tokens=["test", "text"], annotation=annotation, status=status
    )
    assert record.status == expected_status


def test_text_classification_record_none_inputs():
    """Test validation error for None in inputs"""
    with pytest.raises(ValidationError):
        TextClassificationRecord(inputs={"text": None})