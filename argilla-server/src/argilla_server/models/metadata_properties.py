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

from argilla_server.enums import MetadataPropertyType
from argilla_server.errors.future import UnprocessableEntityError
from pydantic import BaseModel, Field

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
    values: Optional[List[Any]] = None

    def check_metadata(self, value: Any) -> None:
        if self.values is None:
            return

        values = value
        if not isinstance(values, list):
            values = [value]

        for v in values:
            if v not in self.values:
                raise UnprocessableEntityError(f"'{v}' is not an allowed term.")


NT = TypeVar("NT", int, float)


class NumericMetadataPropertySettings(BaseMetadataPropertySettings, BaseModel, Generic[NT]):
    min: Optional[NT] = None
    max: Optional[NT] = None

    def check_metadata(self, value: NT) -> None:
        if self.min is not None and value < self.min:
            raise UnprocessableEntityError(f"'{value}' is less than the minimum value of '{self.min}'.")

        if self.max is not None and value > self.max:
            raise UnprocessableEntityError(f"'{value}' is greater than the maximum value of '{self.max}'.")


class IntegerMetadataPropertySettings(NumericMetadataPropertySettings[int]):
    type: Literal[MetadataPropertyType.integer]

    def check_metadata(self, value: int) -> None:
        if not isinstance(value, int):
            raise UnprocessableEntityError(f"'{value}' is not an integer.")

        return super().check_metadata(value)


class FloatMetadataPropertySettings(NumericMetadataPropertySettings[float]):
    type: Literal[MetadataPropertyType.float]

    def check_metadata(self, value: float) -> None:
        if not isinstance(value, float):
            raise UnprocessableEntityError(f"'{value}' is not a float.")

        return super().check_metadata(value)


MetadataPropertySettings = Annotated[
    Union[
        TermsMetadataPropertySettings,
        IntegerMetadataPropertySettings,
        FloatMetadataPropertySettings,
    ],
    Field(..., discriminator="type"),
]
