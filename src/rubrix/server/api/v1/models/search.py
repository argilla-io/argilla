from typing import Generic, List, TypeVar

from pydantic.generics import GenericModel

from rubrix.server.api.v1.models.commons.params import build_pagination_params
from rubrix.server.tasks.commons import BaseRecord

Record = TypeVar("Record", bound=BaseRecord)


class BaseSearchResults(GenericModel, Generic[Record]):
    total: int
    records: List[Record]


PaginationParams = build_pagination_params(item_type="record")
