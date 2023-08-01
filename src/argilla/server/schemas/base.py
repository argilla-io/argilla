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

from typing import Any, Dict, Set, Union

from pydantic import BaseModel, root_validator


class UpdateSchema(BaseModel):
    """Base schema for update endpoints. `__non_nullable_fields__` is a set of fields that cannot be set to `None`
    explicitly. The list of fields is validated in `validate_non_nullable_fields` root validator, which will raise a
    `ValueError` if any of the fields in the set was set to `None` explicitly.
    """

    __non_nullable_fields__: Union[Set[str], None] = None

    @root_validator(pre=True)
    def validate_non_nullable_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if cls.__non_nullable_fields__ is None:
            return values

        invalid_keys = []
        for key in cls.__non_nullable_fields__:
            if key in values and values[key] is None:
                invalid_keys.append(key)

        if invalid_keys:
            raise ValueError(f"The following keys must have non-null values: {', '.join(invalid_keys)}")

        return values
