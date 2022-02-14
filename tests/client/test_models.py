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
import datetime
import json
from typing import Any, Optional

import numpy
import pandas as pd
import pytest
from pydantic import ValidationError

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.client.models import (
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
    _Validators,
)


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
    if status:
        record = TextClassificationRecord(
            inputs={"text": "test"}, annotation=annotation, status=status
        )
    else:
        record = TextClassificationRecord(
            inputs={"text": "test"}, annotation=annotation
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


@pytest.mark.parametrize(
    "prediction,expected",
    [
        (None, None),
        ([("mock", 0, 4)], [("mock", 0, 4, 1.0)]),
        ([("mock", 0, 4, 0.5)], [("mock", 0, 4, 0.5)]),
        (
            [("mock", 0, 4), ("mock", 0, 4, 0.5)],
            [("mock", 0, 4, 1.0), ("mock", 0, 4, 0.5)],
        ),
    ],
)
def test_token_classification_prediction_validator(prediction, expected):
    record = TokenClassificationRecord(
        text="this", tokens=["this"], prediction=prediction
    )
    assert record.prediction == expected


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


def test_model_serialization_with_numpy_nan():
    record = Text2TextRecord(
        text="My name is Sarah and I love my dog.", metadata={"nan": numpy.nan}
    )

    json_record = json.loads(record.json())


def test_warning_when_only_agent():
    class MockRecord(_Validators):
        prediction: Optional[Any] = None
        prediction_agent: Optional[str] = None
        annotation: Optional[Any] = None
        annotation_agent: Optional[str] = None

    with pytest.warns(
        UserWarning, match="`prediction_agent` will not be logged to the server."
    ):
        MockRecord(prediction_agent="mock")
    with pytest.warns(
        UserWarning, match="`annotation_agent` will not be logged to the server."
    ):
        MockRecord(annotation_agent="mock")


def test_forbid_extra():
    class MockRecord(_Validators):
        mock: str

    with pytest.raises(ValidationError):
        MockRecord(mock="mock", extra_argument="mock")


def test_nat_to_none():
    class MockRecord(_Validators):
        event_timestamp: Optional[datetime.datetime] = None

    record = MockRecord(event_timestamp=pd.NaT)
    assert record.event_timestamp is None


@pytest.mark.parametrize(
    "prediction,expected",
    [
        (None, None),
        (["mock"], [("mock", 1.0)]),
        ([("mock", 0.5)], [("mock", 0.5)]),
        (["mock", ("mock", 0.5)], [("mock", 1.0), ("mock", 0.5)]),
    ],
)
def test_text2text_prediction_validator(prediction, expected):
    record = Text2TextRecord(text="mock", prediction=prediction)
    assert record.prediction == expected
