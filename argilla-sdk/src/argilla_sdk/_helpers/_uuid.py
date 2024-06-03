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

from typing import Optional, Union
from uuid import UUID


class UUIDUtilities:
    """A utility for UUID operations with error handling."""

    @staticmethod
    def _uuid_as_str(uuid: UUID) -> str:
        """Converts UUID to string
        Args:
            uuid (UUID): The UUID to convert
        Returns:
            str: The converted string
        """
        try:
            return str(uuid)
        except AttributeError as e:
            raise ValueError(f"Invalid UUID to be converted into string: {uuid}") from e

    @staticmethod
    def _str_as_uuid(uuid: str) -> UUID:
        """Converts string to UUID with and without hyphens.
        Args:
            uuid (str): The string to convert
        Returns:
            UUID: The converted UUID
        """
        try:
            return UUID(uuid)
        except AttributeError as e:
            raise ValueError(f"Invalid str to be converted into UUID: {uuid}") from e

    @classmethod
    def convert_optional_uuid(cls, uuid: Optional[Union[UUID, str]]) -> Optional[UUID]:
        """Converts optional UUID to UUID or leaves as none
        Args:
            uuid (Optional[Union[UUID, str]]): The UUID to convert
        Returns:
            Optional[UUID]: The converted UUID or None
        """
        if isinstance(uuid, UUID):
            return uuid
        elif uuid is None:
            return None
        elif isinstance(uuid, str):
            return cls._str_as_uuid(uuid)
        else:
            raise ValueError(f"Invalid type for UUID: {type(uuid)}")
