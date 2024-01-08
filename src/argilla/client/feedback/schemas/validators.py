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

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from argilla.pydantic_v1 import BaseModel


def title_must_have_value(cls: "BaseModel", v: Optional[str], values: Dict[str, Any]) -> str:
    """Function to add as a `pydantic` validator to a field.

    This function will be called when the field is being validated, and it will
    receive the value of the field, and the values of the model being validated.

    If the field `title` is not empty, then it will be returned as is. Otherwise,
    the value of the field `name` will be capitalized and returned.
    """
    if not v:
        # If `name` doesn't pass the regex validation, then `values` won't have it
        name = values.get("name")
        if name:
            # If `name` has a value, then capitalize it and return it as the `title`
            return name.capitalize()
    return v


def validate_numeric_metadata_property_bounds(cls: "BaseModel", values: Dict[str, Any]) -> Dict[str, Any]:
    name = values.get("name")
    min = values.get("min")
    max = values.get("max")

    if min is not None and max is not None and min >= max:
        raise ValueError(f"`{cls.__name__}` with name={name} cannot have `max` less or equal than `min`")

    return values


def validate_numeric_metadata_filter_bounds(cls: "BaseModel", values: Dict[str, Any]) -> Dict[str, Any]:
    name = values.get("name")
    le = values.get("le")
    ge = values.get("ge")

    if le is None and ge is None:
        raise ValueError(f"`{cls.__name__}` with name={name} must have at least one of `le` or `ge`")

    if le is not None and ge is not None and le < ge:
        raise ValueError(f"`{cls.__name__}` with name={name} cannot have `le` less than `ge`")

    return values
