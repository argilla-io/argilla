from typing import Generic, List, TypeVar

from pydantic.generics import GenericModel

from rubrix.server.tasks.commons import BaseRecord

Record = TypeVar("Record", bound=BaseRecord)


class BaseSearchResults(GenericModel, Generic[Record]):
    total: int
    records: List[Record]
