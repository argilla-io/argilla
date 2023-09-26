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

import dataclasses
import re
from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Iterable, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from argilla.server.enums import ResponseStatus, ResponseStatusFilter
from argilla.server.models import Dataset, MetadataProperty, Record, Response, User

__all__ = [
    "SearchEngine",
    "StringQuery",
    "MetadataFilter",
    "TermsMetadataFilter",
    "IntegerMetadataFilter",
    "FloatMetadataFilter",
    "UserResponseStatusFilter",
    "SearchResponseItem",
    "SearchResponses",
    "SortBy",
]


@dataclasses.dataclass
class StringQuery:
    q: str
    field: Optional[str] = None


@dataclasses.dataclass
class UserResponseStatusFilter:
    user: User
    statuses: List[ResponseStatusFilter]


@dataclasses.dataclass
class MetadataFilter:
    metadata_property: MetadataProperty

    @classmethod
    @abstractmethod
    def from_string(cls, metadata_property: MetadataProperty, string: str) -> "MetadataFilter":
        pass


@dataclasses.dataclass
class TermsMetadataFilter(MetadataFilter):
    values: List[str]

    @classmethod
    def from_string(cls, metadata_property: MetadataProperty, string: str) -> "MetadataFilter":
        return cls(metadata_property=metadata_property, values=string.split(","))


# TODO: transform to `pydantic.BaseModel`
@dataclasses.dataclass
class IntegerMetadataFilter(MetadataFilter):
    low: Optional[int] = None
    high: Optional[int] = None

    class RangeModel(BaseModel):
        from_: Optional[int] = Field(alias="from")
        to: Optional[int]

    def __post_init__(self):
        if self.low is None and self.high is None:
            raise ValueError("One of `low` or `high` value must be provided")

    @classmethod
    def from_string(cls, metadata_property: MetadataProperty, string: str) -> "IntegerMetadataFilter":
        model = cls.RangeModel.parse_raw(string)
        return cls(metadata_property, model.from_, model.to)


# TODO: transform to `pydantic.BaseModel`
@dataclasses.dataclass
class FloatMetadataFilter(MetadataFilter):
    low: Optional[float] = None
    high: Optional[float] = None

    class RangeModel(BaseModel):
        from_: Optional[float] = Field(alias="from")
        to: Optional[float]

    def __post_init__(self):
        if self.low is None and self.high is None:
            raise ValueError("One of `low` or `high` value must be provided")

    @classmethod
    def from_string(cls, metadata_property: MetadataProperty, string: str) -> "FloatMetadataFilter":
        model = cls.RangeModel.parse_raw(string)
        return cls(metadata_property, model.from_, model.to)


@dataclasses.dataclass
class SearchResponseItem:
    record_id: UUID
    score: Optional[float]


@dataclasses.dataclass
class SearchResponses:
    items: List[SearchResponseItem]
    total: int = 0


class SortBy(BaseModel):
    field: Union[MetadataProperty, Literal["inserted_at"], Literal["updated_at"]]
    order: Union[Literal["asc"], Literal["desc"]] = "asc"

    class Config:
        arbitrary_types_allowed = True


class SearchEngine(metaclass=ABCMeta):
    registered_classes = {}

    @classmethod
    @abstractmethod
    async def new_instance(cls) -> "SearchEngine":
        pass

    @abstractmethod
    async def close(self):
        pass

    @classmethod
    def register(cls, engine_name: str):
        def decorator(engine_class):
            cls.registered_classes[engine_name] = engine_class
            return engine_class

        return decorator

    @classmethod
    @asynccontextmanager
    async def get_by_name(cls, engine_name: str) -> AsyncGenerator["SearchEngine", None]:
        engine_name = engine_name.lower().strip()

        if engine_name not in cls.registered_classes:
            raise ValueError(f"No engine class registered for '{engine_name}'")

        engine_class = cls.registered_classes[engine_name]

        engine = None

        try:
            engine = await engine_class.new_instance()
            yield engine
        except Exception as e:
            raise e
        finally:
            if engine is not None:
                await engine.close()

    @abstractmethod
    async def create_index(self, dataset: Dataset):
        pass

    @abstractmethod
    async def delete_index(self, dataset: Dataset):
        pass

    @abstractmethod
    async def configure_metadata_property(self, metadata_property: MetadataProperty):
        pass

    @abstractmethod
    async def add_records(self, dataset: Dataset, records: Iterable[Record]):
        pass

    @abstractmethod
    async def delete_records(self, dataset: Dataset, records: Iterable[Record]):
        pass

    @abstractmethod
    async def update_record_response(self, response: Response):
        pass

    @abstractmethod
    async def delete_record_response(self, response: Response):
        pass

    @abstractmethod
    async def search(
        self,
        dataset: Dataset,
        query: Optional[Union[StringQuery, str]] = None,
        # TODO(@frascuchon): The search records method should receive a generic list of filters
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        metadata_filters: Optional[List[MetadataFilter]] = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: List[SortBy] = None,
    ) -> SearchResponses:
        pass
