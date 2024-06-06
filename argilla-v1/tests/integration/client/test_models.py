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
import uuid
from typing import Any, Optional

import numpy
import pandas as pd
import pytest
from argilla_v1.client.models import (
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
    _Validators,
)
from pydantic import ValidationError


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
        record = TextClassificationRecord(inputs={"text": "test"}, annotation=annotation, status=status)
    else:
        record = TextClassificationRecord(inputs={"text": "test"}, annotation=annotation)
    assert record.status == expected_status


def test_text_classification_input_string():
    record_id = str(uuid.uuid4())
    event_timestamp = datetime.datetime.now()
    assert TextClassificationRecord(
        id=record_id, text="A text", event_timestamp=event_timestamp
    ) == TextClassificationRecord(id=record_id, inputs=dict(text="A text"), event_timestamp=event_timestamp)

    assert TextClassificationRecord(
        id=record_id, inputs=["A text", "another text"], event_timestamp=event_timestamp
    ) == TextClassificationRecord(
        id=record_id, inputs=dict(text=["A text", "another text"]), event_timestamp=event_timestamp
    )


def test_text_classification_text_inputs():
    record_id = str(uuid.uuid4())
    with pytest.raises(ValueError, match="either 'text' or 'inputs'"):
        TextClassificationRecord()

    with pytest.raises(ValueError, match="either 'text' or 'inputs'"):
        TextClassificationRecord(text="mock", inputs={"text": "mock_test"})

    with pytest.warns(
        FutureWarning,
        match=r"the `inputs` argument of the `TextClassificationRecord` will not accept strings.",
    ):
        TextClassificationRecord(inputs="mock")

    event_timestamp = datetime.datetime.now()
    assert TextClassificationRecord(
        id=record_id, text="mock", event_timestamp=event_timestamp
    ) == TextClassificationRecord(id=record_id, inputs={"text": "mock"}, event_timestamp=event_timestamp)

    assert TextClassificationRecord(
        id=record_id, inputs=["mock"], event_timestamp=event_timestamp
    ) == TextClassificationRecord(id=record_id, inputs={"text": ["mock"]}, event_timestamp=event_timestamp)

    assert TextClassificationRecord(
        id=record_id, text="mock", inputs={"text": "mock"}, event_timestamp=event_timestamp
    ) == TextClassificationRecord(id=record_id, inputs={"text": "mock"}, event_timestamp=event_timestamp)

    rec = TextClassificationRecord(text="mock")
    with pytest.raises(AttributeError, match="You cannot assign a new value to `text`"):
        rec.text = "mock"
    with pytest.raises(AttributeError, match="You cannot assign a new value to `inputs`"):
        rec.inputs = "mock"


@pytest.mark.parametrize(
    ("annotation", "status", "expected_status", "expected_iob"),
    [
        (None, None, "Default", None),
        ([("test", 0, 4)], None, "Validated", ["B-test", "O"]),
        (None, "Discarded", "Discarded", None),
        ([("test", 0, 9)], "Discarded", "Discarded", ["B-test", "I-test"]),
    ],
)
def test_token_classification_record(annotation, status, expected_status, expected_iob):
    """Just testing its dynamic defaults"""
    record = TokenClassificationRecord(text="test text", tokens=["test", "text"], annotation=annotation, status=status)
    assert record.status == expected_status
    assert record.spans2iob(record.annotation) == expected_iob


@pytest.mark.parametrize(
    ("tokens", "tags", "annotation"),
    [
        (["Una", "casa"], ["O", "B-OBJ"], [("OBJ", 4, 8)]),
        (["Matias", "Aguado"], ["B-PER", "I-PER"], [("PER", 0, 13)]),
        (["Todo", "Todo", "Todo"], ["B-T", "I-T", "L-T"], [("T", 0, 14)]),
        (["Una", "casa"], ["O", "U-OBJ"], [("OBJ", 4, 8)]),
        (["Todo", "Todo", "Todo"], ["I-T", "I-T", "O"], [("T", 0, 9)]),
    ],
)
def test_token_classification_with_tokens_and_tags(tokens, tags, annotation):
    record = TokenClassificationRecord(tokens=tokens, tags=tags)
    assert record.annotation is not None
    assert record.annotation == annotation


def test_token_classification_validations():
    with pytest.raises(
        AssertionError,
        match=("Missing fields: " "At least one of `text` or `tokens` argument must be provided!"),
    ):
        TokenClassificationRecord()

    tokens = ["test", "text"]
    annotation = [("test", 0, 4)]
    with pytest.raises(
        AssertionError,
        match=("Missing field `text`: " "char level spans must be provided with a raw text sentence"),
    ):
        TokenClassificationRecord(tokens=tokens, annotation=annotation)

    with pytest.raises(
        AssertionError,
        match=("Missing field `text`: " "char level spans must be provided with a raw text sentence"),
    ):
        TokenClassificationRecord(tokens=tokens, prediction=annotation)

    TokenClassificationRecord(text=" ".join(tokens), tokens=tokens, prediction=annotation)

    record = TokenClassificationRecord(tokens=tokens)
    assert record.text == "test text"


def test_token_classification_with_mutation():
    text_a = "The text"
    text_b = "Another text sample here !!!"

    record = TokenClassificationRecord(text=text_a, tokens=text_a.split(" "), annotation=[])
    assert record.spans2iob(record.annotation) == ["O"] * len(text_a.split(" "))

    with pytest.raises(AttributeError, match="You cannot assign a new value to `text`"):
        record.text = text_b
    with pytest.raises(AttributeError, match="You cannot assign a new value to `tokens`"):
        record.tokens = text_b.split(" ")


@pytest.mark.parametrize(
    "prediction,expected",
    [
        (None, None),
        ([("mock", 0, 4)], [("mock", 0, 4, 0.0)]),
        ([("mock", 0, 4, 0.5)], [("mock", 0, 4, 0.5)]),
        ([("mock", 0, 4, None)], [("mock", 0, 4, 0.0)]),
        (
            [("mock", 0, 4), ("mock", 0, 4, None), ("mock", 0, 4, 0.5)],
            [("mock", 0, 4, 0.0), ("mock", 0, 4, 0.0), ("mock", 0, 4, 0.5)],
        ),
    ],
)
def test_token_classification_prediction_validator(prediction, expected):
    record = TokenClassificationRecord(text="this", tokens=["this"], prediction=prediction)
    assert record.prediction == expected


def test_text_classification_record_none_inputs():
    """Test validation error for None in inputs"""
    with pytest.raises(ValidationError):
        TextClassificationRecord.parse_obj(dict(inputs={"text": None}))


def test_metadata_values_length():
    text = "oh yeah!"
    expected_length = 200
    metadata = {"too_long": "a" * expected_length}

    with pytest.warns(expected_warning=UserWarning):
        record = TextClassificationRecord(
            inputs={"text": text},
            metadata=metadata,
        )
    assert len(record.metadata["too_long"]) == expected_length

    with pytest.warns(expected_warning=UserWarning):
        record = TokenClassificationRecord(
            text=text,
            tokens=text.split(),
            metadata=metadata,
        )
    assert len(record.metadata["too_long"]) == expected_length


def test_model_serialization_with_numpy_nan():
    record = Text2TextRecord(text="My name is Sarah and I love my dog.", metadata={"nan": numpy.nan})

    json.loads(record.json())


def test_warning_when_only_agent():
    class MockRecord(_Validators):
        prediction: Optional[Any] = None
        prediction_agent: Optional[str] = None
        annotation: Optional[Any] = None
        annotation_agent: Optional[str] = None

    with pytest.warns(UserWarning, match="`prediction_agent` will not be logged to the server."):
        MockRecord(prediction_agent="mock")
    with pytest.warns(UserWarning, match="`annotation_agent` will not be logged to the server."):
        MockRecord(annotation_agent="mock")


def test_forbid_extra():
    class MockRecord(_Validators):
        mock: str

    with pytest.raises(ValidationError):
        MockRecord(mock="mock", extra_argument="mock")


def test_none_to_datetime():
    class MockRecord(_Validators):
        event_timestamp: Optional[datetime.datetime] = None

    record = MockRecord()
    assert isinstance(record.event_timestamp, datetime.datetime)


def test_none_id_to_uid():
    class MockRecord(_Validators):
        id: Optional[str] = None

    record = MockRecord()
    assert isinstance(record.id, str)


def test_nat_to_none_to_datetime():
    class MockRecord(_Validators):
        event_timestamp: Optional[datetime.datetime] = None

    record = MockRecord(event_timestamp=pd.NaT)
    assert isinstance(record.event_timestamp, datetime.datetime)


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


@pytest.mark.parametrize(
    "record",
    [
        TextClassificationRecord(text="This is a test"),
        TokenClassificationRecord(text="This is a test", tokens="This is a test".split()),
        Text2TextRecord(text="This is a test"),
    ],
)
def test_record_validation_on_assignment(record):
    with pytest.raises(ValidationError):
        record.prediction = "rubbish"

    with pytest.raises(ValidationError):
        record.annotation = [("rubbish",)]

    with pytest.raises(ValidationError):
        record.vectors = "rubbish"


def test_cast_record_id():
    record_id = 1000

    with pytest.warns(
        DeprecationWarning,
        match=r"Integer ids won't be supported in future versions. We recommend to start using strings instead. ",
    ):
        record = TextClassificationRecord(text="This is a text", id=record_id)
        assert record.id == record_id


def test_big_integer_record_id():
    import random

    record_id = random.getrandbits(64)
    with pytest.warns(
        UserWarning,
        match=r"You've provided a big integer value. Use a string instead, otherwise you may experience some ",
    ):
        record = TextClassificationRecord(text="This is a text", id=record_id)
        assert record.id == record_id


def test_create_record_with_wrong_id_type():
    with pytest.raises(ValidationError):
        TextClassificationRecord(text="This is a text", id=uuid.uuid4())
