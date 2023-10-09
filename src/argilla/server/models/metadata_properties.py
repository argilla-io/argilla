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

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from argilla.server.enums import MetadataPropertyType

__all__ = [
    "MetadataPropertySettings",
    "TermsMetadataPropertySettings",
    "IntegerMetadataPropertySettings",
    "FloatMetadataPropertySettings",
]

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


class BaseMetadataPropertySettings(BaseModel, ABC):
    @abstractmethod
    def check_metadata(self, value: Any) -> None:
        pass


class TermsMetadataPropertySettings(BaseMetadataPropertySettings):
    type: Literal[MetadataPropertyType.terms]
    values: List[str]

    def check_metadata(self, value: str) -> None:
        if value not in self.values:
            raise ValueError(f"'{value}' is not an allowed term.")


NT = TypeVar("NT", int, float)


class NumericMetadataPropertySettings(BaseMetadataPropertySettings, Generic[NT]):
    min: Optional[NT] = None
    max: Optional[NT] = None

    def check_metadata(self, value: NT) -> None:
        if self.min is not None and value < self.min:
            raise ValueError(f"'{value}' is less than the minimum value of '{self.min}'.")

        if self.max is not None and value > self.max:
            raise ValueError(f"'{value}' is greater than the maximum value of '{self.max}'.")


class IntegerMetadataPropertySettings(NumericMetadataPropertySettings[int]):
    type: Literal[MetadataPropertyType.integer]


class FloatMetadataPropertySettings(NumericMetadataPropertySettings[float]):
    type: Literal[MetadataPropertyType.float]


MetadataPropertySettings = Annotated[
    Union[
        TermsMetadataPropertySettings,
        IntegerMetadataPropertySettings,
        FloatMetadataPropertySettings,
    ],
    Field(..., discriminator="type"),
]
