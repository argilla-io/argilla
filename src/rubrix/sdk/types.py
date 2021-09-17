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

""" Contains some shared types for properties """

from typing import (
    BinaryIO,
    Generic,
    MutableMapping,
    Optional,
    TextIO,
    Tuple,
    TypeVar,
    Union,
)

import attr


class Unset:
    def __bool__(self) -> bool:
        return False


UNSET: Unset = Unset()


@attr.s(auto_attribs=True)
class File:
    """Contains information for file uploads"""

    payload: Union[BinaryIO, TextIO]
    file_name: Optional[str] = None
    mime_type: Optional[str] = None

    def to_tuple(self) -> Tuple[Optional[str], Union[BinaryIO, TextIO], Optional[str]]:
        """Return a tuple representation that httpx will accept for multipart/form-data"""
        return self.file_name, self.payload, self.mime_type


T = TypeVar("T")


@attr.s(auto_attribs=True)
class Response(Generic[T]):
    """A response from an endpoint"""

    status_code: int
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[T]


__all__ = ["File", "Response"]
