#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest
from pydantic import ValidationError
from rubrix._constants import MAX_KEYWORD_LENGTH

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


def test_text_classification_input_string():
    assert TextClassificationRecord(inputs="A text") == TextClassificationRecord(
        inputs=dict(text="A text")
    )

    assert TextClassificationRecord(
        inputs=["A text", "another text"]
    ) == TextClassificationRecord(inputs=dict(text=["A text", "another text"]))


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


def test_metadata_values_length():
    text = "oh yeah!"
    metadata = {"too_long": "a" * 200}

    record = TextClassificationRecord(inputs={"text": text}, metadata=metadata)
    assert len(record.metadata["too_long"]) == MAX_KEYWORD_LENGTH

    record = TokenClassificationRecord(
        text=text, tokens=text.split(), metadata=metadata
    )
    assert len(record.metadata["too_long"]) == MAX_KEYWORD_LENGTH
