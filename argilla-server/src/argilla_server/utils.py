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

import re
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException, Query

from argilla_server.pydantic_v1 import BaseModel


# TODO: remove this function at some point
def parse_uuids(uuids_str: str) -> List[UUID]:
    try:
        return [UUID(uuid_str) for uuid_str in uuids_str.split(",")]
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")


T = TypeVar("T", bound=BaseModel)

# Matches key1,key2,key3 and key:value1,value2,value3, but not key1,key2,key3:value1,value2,value3
PARAM_REGEX = re.compile(r"^(?:(?:[^,:]+(?:,[^,:]+)*)|(?:[^,:]+:[^,:]+(?:,[^,:]+)*))$")


def parse_query_param(
    name: str,
    max_keys: Optional[int] = None,
    max_values_per_key: Optional[int] = None,
    model: Optional[Type[T]] = None,
    group_keys_without_values: bool = True,
    **kwargs: Any,
) -> Callable[[Optional[List[str]]], Union[Dict[str, Any], T, None]]:
    """Generates a function that can be used as a FastAPI dependency (`fastapi.Depends`) and that parses the values of
    a query parameter with the following format:

        `...?param_name=key1&param_name=key2&param_name=key3,key4&param_name=key5:value1,value2,value3`

    The values are parsed into a dictionary with the following structure:

        ```python
        {
            "keys": ["key1", "key2", "key3", "key4"],
            "key5": ["value1", "value2", "value3"]
        }
        ```

    or, if `max_keys` is set to 1:

        ```python
        {
            "key": "key1",
            "value": ["value1", "value2", "value3"]
        }
        ```

    or, if `group_keys_without_values` is set to `False`:

        ```python
        {
            "key1": None,
            "key2": None,
            "key3": None,
            "key4": None,
            "key5": ["value1", "value2", "value3"]
        }
        ```

    In addition, if a `pydantic.BaseModel` is provided, the dictionary is parsed into an instance of that model:

        ```python
        from argilla_server.pydantic_v1 import BaseModel, Field


        class Params(BaseModel):
            keys: List[str] = Field(..., alias="keys")
            my_other_key_with_values: List[str] = Field(..., alias="key5")
        ```

    Args:
        name: name of the query parameter.
        max_keys: maximum number of keys allowed in the query parameter. Defaults to `None`.
        max_values_per_key: maximum number of values per key allowed in the query parameter. Defaults to `None`.
        model: optional `pydantic.BaseModel` to parse the query parameter into. Defaults to `None`.
        kwargs: extra parameters for `pydantic.Query` function.

    Returns:
        A function that parses the query parameter into a dictionary or a `pydantic.BaseModel` instance.
    """

    # Doing this for the correctness of the OpenAPI schema
    if max_keys is not None and max_keys == 1:
        query_param_typing = Optional[str]
    else:
        query_param_typing = Optional[List[str]]

    def _parse(
        param_values: Optional[query_param_typing] = Query(None, alias=name, **kwargs),
    ) -> Union[Dict[str, Any], T, None]:
        if param_values is None:
            return None

        if isinstance(param_values, str):
            param_values = [param_values]

        parsed_params: Dict[str, Any] = defaultdict(list)
        for value in param_values:
            if not PARAM_REGEX.match(value):
                raise HTTPException(
                    status_code=422,
                    detail=f"'{name}' query parameter must be of the form 'key1,key2,key3' or 'key:value1,value2,value3'",
                )

            parts = value.split(":")
            num_parts = len(parts)
            if num_parts == 1:
                parts = parts[0].split(",")
                if group_keys_without_values:
                    parsed_params["keys"].extend(parts)
                else:
                    for part in parts:
                        parsed_params[part] = None
            else:
                key = parts[0]
                values = parts[1].split(",")
                parsed_params[key].extend(values)

        # Check that the number of keys is within the allowed range
        num_keys_without_values = len(parsed_params.get("keys", []))
        num_keys_with_values = len(parsed_params) - 1  # we don't want to count the "keys" key
        total_keys = num_keys_with_values + num_keys_without_values
        if max_keys is not None and total_keys > max_keys:
            raise HTTPException(
                status_code=422, detail=f"'{name}' query parameter must contain at most {max_keys} comma-separated keys"
            )

        # Check that the number of values per key is within the allowed range
        if max_values_per_key is not None:
            for key, values in parsed_params.items():
                if key == "keys":
                    continue

                num_values = len(values) if values is not None else 0
                if num_values > max_values_per_key:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"'{name}' query parameter must contain at most {max_values_per_key} values per"
                            f" comma-separated key. '{key}' has {num_values} values."
                        ),
                    )

                if num_values == 1:
                    parsed_params[key] = values[0]

        # If `max_keys == 1`, we want to return a dictionary with just `key` and `value` keys
        if max_keys == 1:
            if num_keys_without_values == 1:
                parsed_params["key"] = parsed_params["keys"].pop()
                del parsed_params["keys"]
            else:
                key, value = next(iter(parsed_params.items()))
                parsed_params["key"] = key
                parsed_params["value"] = value
                del parsed_params[key]

        if model is not None:
            return model(**parsed_params)

        return parsed_params

    return _parse
