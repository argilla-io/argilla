import dataclasses
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Iterable, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from argilla.server.enums import ResponseStatus, ResponseStatusFilter
from argilla.server.models import Dataset, Record, Response, User


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

