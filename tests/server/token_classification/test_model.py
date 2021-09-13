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


def test_too_long_metadata():
    text = "On one ones o no"
    record = TokenClassificationRecord.parse_obj(
        {
            "text": text,
            "tokens": text.split(),
            "metadata": {"too_long": "a"*1000},
        }
    )

    assert len(record.metadata["too_long"]) == MAX_KEYWORD_LENGTH


def test_entity_label_too_long():
    text = "On one ones o no"
    with pytest.raises(
        ValidationError, match="ensure this value has at most 128 character"
    ):
        TokenClassificationRecord(
            text=text,
            tokens=text.split(),
            prediction=TokenClassificationAnnotation(
                agent="test",
                entities=[
                    EntitySpan(
                        start=9,
                        end=len(text),
                        label="a"*1000,
                    ),
                ],
            ),
        )
