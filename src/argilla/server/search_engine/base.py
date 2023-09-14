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
from abc import ABCMeta, abstractmethod
from typing import Any, AsyncGenerator, Dict, Iterable, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, conint

from argilla.server.enums import ResponseStatus, ResponseStatusFilter
from argilla.server.models import Dataset, Record, Response, User, Vector, VectorSettings

__all__ = [
    "SearchEngine",
    "UserResponse",
    "StringQuery",
    "UserResponseStatusFilter",
    "SearchResponseItem",
    "SearchResponses",
]


class UserResponse(BaseModel):
    values: Optional[Dict[str, Any]]
    status: ResponseStatus


@dataclasses.dataclass
class StringQuery:
    q: str
    field: Optional[str] = None


@dataclasses.dataclass
class UserResponseStatusFilter:
    user: User
    statuses: List[ResponseStatusFilter]


@dataclasses.dataclass
class SearchResponseItem:
    record_id: UUID
    score: Optional[float]


@dataclasses.dataclass
class SearchResponses:
    items: List[SearchResponseItem]
    total: int = 0


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
    async def search_engine_by_name(cls, engine_name: str) -> AsyncGenerator["SearchEngine", None]:
        engine_name = engine_name.lower().strip()

        if engine_name not in cls.registered_classes:
            raise ValueError(f"No engine class registered for '{engine_name}'")

        engine_class = cls.registered_classes[engine_name]

        try:
            engine = await engine_class.new_instance()
            yield engine
        finally:
            await engine.close()

    @abstractmethod
    async def create_index(self, dataset: Dataset):
        pass

    @abstractmethod
    async def delete_index(self, dataset: Dataset):
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
        query: Union[StringQuery, str],
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> SearchResponses:
        pass

    @abstractmethod
    async def configure_index_vectors(self, vector_settings: VectorSettings):
        pass

    @abstractmethod
    async def set_records_vectors(self, dataset: Dataset, vectors: Iterable[Vector]):
        pass

    @abstractmethod
    async def similarity_search(
        self,
        dataset: Dataset,
        vector_settings: VectorSettings,
        value: Optional[List[float]] = None,
        record: Optional[Record] = None,
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        max_results: conint(ge=2, le=500) = 100,
        threshold: Optional[float] = None,
    ) -> SearchResponses:
        pass
