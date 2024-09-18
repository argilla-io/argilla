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

from typing import Any

import pytest
from argilla_server.api.schemas.v1.responses import (
    RankingQuestionResponseValueItem,
    ResponseValueCreate,
    SpanQuestionResponseValueItem,
)


class TestResponseValueCreate:
    @pytest.mark.parametrize("value", ["hello", "0", "42", "42.0", "42.5", "-1", "True", "False"])
    def test_with_string_value(self, value: str):
        assert isinstance(ResponseValueCreate(value=value).value, str)

    @pytest.mark.parametrize("value", [1, 2, 3, 42])
    def test_with_int_value(self, value: int):
        assert isinstance(ResponseValueCreate(value=value).value, int)

    def test_with_list_value(self):
        assert ResponseValueCreate(value=[]).value == []
        assert ResponseValueCreate(value=["1", "2", "3"]).value == ["1", "2", "3"]
        assert ResponseValueCreate(value=[1.0, 2.0, 3.0]).value == ["1.0", "2.0", "3.0"]

    def test_with_ranking_value(self):
        assert ResponseValueCreate(value=[{"value": "value-1"}]).value == [
            RankingQuestionResponseValueItem(value="value-1")
        ]
        assert ResponseValueCreate(value=[{"value": "value-1", "rank": 1}]).value == [
            RankingQuestionResponseValueItem(value="value-1", rank=1)
        ]
        assert ResponseValueCreate(value=[{"value": "value-1", "rank": 1}, {"value": "value-2", "rank": 2}]).value == [
            RankingQuestionResponseValueItem(value="value-1", rank=1),
            RankingQuestionResponseValueItem(value="value-2", rank=2),
        ]

    def test_with_span_value(self):
        assert ResponseValueCreate(value=[{"label": "label-1", "start": 0, "end": 1}]).value == [
            SpanQuestionResponseValueItem(label="label-1", start=0, end=1)
        ]
        assert ResponseValueCreate(
            value=[
                {"label": "label-1", "start": 0, "end": 1},
                {"label": "label-2", "start": 42, "end": 69},
            ]
        ).value == [
            SpanQuestionResponseValueItem(label="label-1", start=0, end=1),
            SpanQuestionResponseValueItem(label="label-2", start=42, end=69),
        ]

    @pytest.mark.parametrize("value", [True, False, 0.0, 42.0, {}])
    def test_with_invalid_value(self, value: Any):
        with pytest.raises(Exception):
            ResponseValueCreate(value=value)
