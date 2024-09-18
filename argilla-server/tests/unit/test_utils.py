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

from typing import Any, Dict, List, Set
from fastapi import HTTPException
from pydantic import BaseModel, Field

from argilla_server.utils import parse_query_param


@pytest.mark.parametrize(
    "config, params, expected",
    [
        ({}, ["key1", "key2", "key3"], {"keys": ["key1", "key2", "key3"]}),
        ({}, ["key1,key2,key3"], {"keys": ["key1", "key2", "key3"]}),
        ({}, ["key1:value1,value2,value3"], {"key1": ["value1", "value2", "value3"]}),
        (
            {},
            ["key1:value1,value2,value3", "key2:value4,value5,value6"],
            {"key1": ["value1", "value2", "value3"], "key2": ["value4", "value5", "value6"]},
        ),
        ({}, ["key1", "key2", "key3:value1,value2"], {"keys": ["key1", "key2"], "key3": ["value1", "value2"]}),
        ({}, ["key1:value1", "key1:value2"], {"key1": ["value1", "value2"]}),
        ({"max_keys": 1}, ["key1"], {"key": "key1"}),
        ({"max_keys": 1}, ["key1:value1,value2,value3"], {"key": "key1", "value": ["value1", "value2", "value3"]}),
        ({"max_keys": 1, "max_values_per_key": 1}, ["key1:value1"], {"key": "key1", "value": "value1"}),
        ({"max_values_per_key": 1}, ["key1:value1", "key2:value2"], {"key1": "value1", "key2": "value2"}),
        ({"max_values_per_key": 1, "group_keys_without_values": False}, ["key1", "key2"], {"key1": None, "key2": None}),
        ({"group_keys_without_values": False}, ["key1,key2,key3"], {"key1": None, "key2": None, "key3": None}),
        ({"group_keys_without_values": True}, ["key1,key2,key3"], {"keys": ["key1", "key2", "key3"]}),
    ],
)
def test_parse_query_param(config: Dict[str, Any], params: List[str], expected: Dict[str, Set[str]]) -> None:
    parse_function = parse_query_param(name="unit-test", **config)
    result = parse_function(param_values=params)
    assert result == expected


def test_parse_query_param_with_base_model() -> None:
    class Params(BaseModel):
        keys: List[str] = Field(..., alias="keys")
        my_other_key_with_values: List[str] = Field(..., alias="key5")

    parse_function = parse_query_param(name="unit-test", model=Params)
    result = parse_function(param_values=["key1", "key2", "key3,key4", "key5:value1,value2,value3"])
    assert sorted(result.keys) == ["key1", "key2", "key3", "key4"]
    assert sorted(result.my_other_key_with_values) == ["value1", "value2", "value3"]


@pytest.mark.parametrize(
    "config, params, expected_msg",
    [
        (
            {},
            ["key1,key2,key3:value1,value2,value3"],
            "'unit-test' query parameter must be of the form 'key1,key2,key3' or 'key:value1,value2,value3'",
        ),
        ({"max_keys": 1}, ["key1,key2"], "'unit-test' query parameter must contain at most 1 comma-separated keys"),
        (
            {"max_values_per_key": 2},
            ["key1:value1,value2,value3"],
            "'unit-test' query parameter must contain at most 2 values per comma-separated key. 'key1' has 3 values.",
        ),
    ],
)
def test_parse_query_param_raises_http_exception(config: Dict[str, Any], params: List[str], expected_msg: str) -> None:
    parse_function = parse_query_param(name="unit-test", **config)

    with pytest.raises(HTTPException, match="") as exc_info:
        parse_function(param_values=params)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == expected_msg
