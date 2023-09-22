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

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException, Query
from pydantic import BaseModel


def parse_uuids(uuids_str: str) -> List[UUID]:
    try:
        return [UUID(uuid_str) for uuid_str in uuids_str.split(",")]
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")


T = TypeVar("T", bound=BaseModel)


def parse_query_param(
    name: str, help: str, model: Optional[Type[T]] = None
) -> Callable[[Optional[List[str]]], Union[Dict[str, Any], T, None]]:
    """Generates a function that can be used as a FastAPI dependency (`fastapi.Depends`) and that parses the values of
    a query parameter with the following format:

        `...?param_name=key1&param_name=key2&param_name=key3:value1,value2,value3`

    The values are parsed into a dictionary with the following structure:

        ```python
        {
            "keys": ["key1", "key2"],
            "key3": ["value1", "value2", "value3"]
        }
        ```

    In addition, if a `pydantic.BaseModel` is provided, the dictionary is parsed into an instance of that model.

    Args:
        name: name of the query parameter.
        help: help text for the query parameter.
        model: optional `pydantic.BaseModel` to parse the query parameter into. Defaults to `None`.

    Returns:
        A function that parses the query parameter into a dictionary or a `pydantic.BaseModel` instance.
    """

    def _parse(
        param_values: Optional[List[str]] = Query(None, alias=name, description=help)
    ) -> Union[Dict[str, Any], T, None]:
        if param_values is None:
            return None

        parsed_params = defaultdict(list)
        for value in param_values:
            parts = value.split(":")
            if len(parts) == 1:
                parsed_params["keys"].append(parts[0])
            else:
                key = parts[0]
                values = parts[1].split(",")
                parsed_params[key] = values

        if model is not None:
            return model(**parsed_params)

        return parsed_params

    return _parse
