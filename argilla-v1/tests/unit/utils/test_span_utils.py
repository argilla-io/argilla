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
from argilla_v1.utils.span_utils import SpanUtils


def test_init():
    text = "test this."
    tokens = ["test", "this", "."]

    span_utils = SpanUtils(text, tokens)

    assert span_utils.text is text
    assert span_utils.tokens is tokens

    assert span_utils.token_to_char_idx == {0: (0, 4), 1: (5, 9), 2: (9, 10)}
    assert span_utils.char_to_token_idx == {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 2,
    }

    assert span_utils._start_to_token_idx == {0: 0, 5: 1, 9: 2}
    assert span_utils._end_to_token_idx == {4: 0, 9: 1, 10: 2}


def test_init_value_error():
    with pytest.raises(ValueError, match="Token 'ValueError' not found in text: test error"):
        SpanUtils(text="test error", tokens=["test", "ValueError"])


def test_validate():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    assert span_utils.validate([("mock", 5, 10)]) is None


def test_validate_not_valid_spans():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    with pytest.raises(ValueError, match="Following entity spans are not valid: \[\('mock', 2, 1\)\]\n"):
        span_utils.validate([("mock", 2, 1)])


def test_validate_misaligned_spans():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    with pytest.raises(
        ValueError,
        match="Following entity spans are not aligned with provided tokenization\n"
        r"Spans:\n\('mock', 0, 5\) - 'test '\n"
        r"Tokens:\n\['test', 'this', '.'\]",
    ):
        span_utils.validate([("mock", 0, 5)])


def test_validate_not_valid_and_misaligned_spans():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    with pytest.raises(
        ValueError,
        match=r"Following entity spans are not valid: \[\('mock', 2, 1\)\]\n"
        "Following entity spans are not aligned with provided tokenization\n"
        r"Spans:\n\('mock', 0, 5\) - 'test '\n"
        r"Tokens:\n\['test', 'this', '.'\]",
    ):
        span_utils.validate([("mock", 2, 1), ("mock", 0, 5)])


@pytest.mark.parametrize(
    "spans, expected",
    [
        ([("mock", -1, 4), ("mock", 20, 22)], [("mock", 0, 4), ("mock", 20, 21)]),
        ([("mock", 0, 5), ("mock", 4, 9)], [("mock", 0, 4), ("mock", 5, 9)]),
        ([("mock", 10, 15), ("mock", 11, 16)], [("mock", 11, 15), ("mock", 11, 15)]),
    ],
)
def test_correct(spans, expected):
    text = "test this \nnext\ttext."
    tokens = ["test", "this", "\n", "next", "\t", "text", "."]
    span_utils = SpanUtils(text, tokens)

    assert span_utils.correct(spans) == expected


def test_to_tags_overlapping_spans():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    with pytest.raises(ValueError, match="IOB tags cannot handle overlapping spans!"):
        span_utils.to_tags([("mock", 0, 4), ("mock", 0, 9)])


def test_to_tags():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    tags = span_utils.to_tags([("mock", 0, 9)])
    assert tags == ["B-mock", "I-mock", "O"]


def test_from_tags_wrong_length():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    with pytest.raises(
        ValueError,
        match="The list of tags must have the same length as the list of tokens!",
    ):
        span_utils.from_tags(["mock", "mock"])


def test_from_tags_not_valid_format():
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    with pytest.raises(ValueError, match="Tags are not in the IOB or BILOU format!"):
        span_utils.from_tags(["mock", "mock", "mock"])


@pytest.mark.parametrize(
    "tags,expected",
    [
        (["B-mock", "O", "O"], [("mock", 0, 4)]),
        (["I-mock", "O", "O"], [("mock", 0, 4)]),
        (["U-mock", "O", "O"], [("mock", 0, 4)]),
        (["L-mock", "O", "O"], [("mock", 0, 4)]),
        (["B-mock", "I-mock", "O"], [("mock", 0, 9)]),
        (["I-mock", "I-mock", "O"], [("mock", 0, 9)]),
        (["B-mock", "L-mock", "O"], [("mock", 0, 9)]),
        (["I-mock", "L-mock", "O"], [("mock", 0, 9)]),
        (["B-mock", "I-mock", "I-mock"], [("mock", 0, 10)]),
        (["I-mock", "I-mock", "I-mock"], [("mock", 0, 10)]),
        (["B-mock", "I-mock", "L-mock"], [("mock", 0, 10)]),
        (["B-mock", "L-mock", "L-mock"], [("mock", 0, 9), ("mock", 9, 10)]),
        (["U-mock", "U-mock", "O"], [("mock", 0, 4), ("mock", 5, 9)]),
        (["U-mock", "I-mock", "O"], [("mock", 0, 4), ("mock", 5, 9)]),
        (["B-mock", "B-mock", "O"], [("mock", 0, 4), ("mock", 5, 9)]),
        (["U-mock", "B-mock", "O"], [("mock", 0, 4), ("mock", 5, 9)]),
        (["I-mock", "B-mock", "O"], [("mock", 0, 4), ("mock", 5, 9)]),
        (["L-mock", "B-mock", "O"], [("mock", 0, 4), ("mock", 5, 9)]),
    ],
)
def test_from_tags(tags, expected):
    span_utils = SpanUtils("test this.", ["test", "this", "."])
    assert span_utils.from_tags(tags) == expected
