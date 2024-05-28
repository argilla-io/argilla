# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from dataclasses import fields, dataclass
from typing import Type, TypeVar

__all__ = ["dataclass_instance_from_dict"]

T = TypeVar("T", bound=dataclass)


def dataclass_instance_from_dict(cls: Type[T], data: dict) -> T:
    """Create a dataclass instance from a dictionary, ignoring extra keys found in the dictionary."""

    field_names = set(f.name for f in fields(cls))
    return cls(**{k: v for k, v in data.items() if k in field_names})
