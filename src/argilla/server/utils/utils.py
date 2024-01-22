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
from typing import Any


def limit_value_length(data: Any, max_length: int) -> Any:
    """
    Given an input data, limits string values to a max_length by fetching
    last max_length characters

    Parameters
    ----------
    data:
        Input data
    max_length:
        Max length for string values

    Returns
    -------
        Limited version of data, if any
    """

    if isinstance(data, str):
        return data[-max_length:]
    if isinstance(data, dict):
        return {k: limit_value_length(v, max_length=max_length) for k, v in data.items()}
    if isinstance(data, (list, tuple, set)):
        new_values = map(lambda x: limit_value_length(x, max_length=max_length), data)
        return type(data)(new_values)
    return data
