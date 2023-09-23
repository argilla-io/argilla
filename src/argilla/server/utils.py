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
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException, Query
from pydantic import BaseModel


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
    name: str, model: Optional[Type[T]] = None, **kwargs: Any
) -> Callable[[Optional[List[str]]], Union[Dict[str, Any], T, None]]:
    """Generates a function that can be used as a FastAPI dependency (`fastapi.Depends`) and that parses the values of
    a query parameter with the following format:

        `...?param_name=key1&param_name=key2&param_name=key3,key4&param_name=key5:value1,value2,value3`

    The values are parsed into a dictionary with the following structure:

        ```python
        {
            "keys": {"key1", "key2", "key3", "key4"},
            "key5": {"value1", "value2", "value3"}
        }
        ```

    In addition, if a `pydantic.BaseModel` is provided, the dictionary is parsed into an instance of that model:

        ```python
        from pydantic import BaseModel, Field


        class Params(BaseModel):
            keys: List[str] = Field(..., alias="keys")
            my_other_key_with_values: List[str] = Field(..., alias="key5")
        ```

    Args:
        name: name of the query parameter.
        model: optional `pydantic.BaseModel` to parse the query parameter into. Defaults to `None`.
        kwargs: extra parameters for `pydantic.Query` function.

    Returns:
        A function that parses the query parameter into a dictionary or a `pydantic.BaseModel` instance.
    """

    def _parse(param_values: Optional[List[str]] = Query(None, alias=name, **kwargs)) -> Union[Dict[str, Any], T, None]:
        if param_values is None:
            return None

        parsed_params: Dict[str, Set[str]] = defaultdict(set)
        for value in param_values:
            if not PARAM_REGEX.match(value):
                raise HTTPException(
                    status_code=422,
                    detail="'include' query parameter must be of the form 'key1,key2,key3' or 'key:value1,value2,value3'",
                )

            parts = value.split(":")
            if len(parts) == 1:
                parts = parts[0].split(",")
                parsed_params["keys"].update(parts)
            else:
                key = parts[0]
                values = parts[1].split(",")
                parsed_params[key].update(values)

        if model is not None:
            return model(**parsed_params)

        return parsed_params

    return _parse
