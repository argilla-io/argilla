from dataclasses import dataclass

from fastapi import Depends, Path

from rubrix.server.api.v1.constants import DATASET_NAME_PATTERN
from rubrix.server.api.v1.models.commons.task import TaskType
from rubrix.server.commons.api import CommonTaskQueryParams as _CommonTaskQueryParams
from rubrix.server.tasks.commons import PaginationParams as _PaginationParams


@dataclass
class CommonTaskQueryParams(_CommonTaskQueryParams):
    pass


@dataclass
class PaginationParams(_PaginationParams):
    pass


@dataclass
class NameEndpointHandlerParams:
    name: str = Path(..., regex=DATASET_NAME_PATTERN)
    common: CommonTaskQueryParams = Depends()


@dataclass
class TaskNameEndpointHandlerParams:

    task: TaskType = Path(...)
    name: str = Path(..., regex=DATASET_NAME_PATTERN)
    common: CommonTaskQueryParams = Depends()
