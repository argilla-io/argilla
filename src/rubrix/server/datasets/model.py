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

"""
Dataset models definition
"""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from rubrix.server.metrics.model import DatasetMetricDB
from rubrix.server.tasks.commons import TaskType


class UpdateDatasetRequest(BaseModel):
    """
    Modifiable fields for dataset

    Attributes:
    -----------
    tags:
        Dataset tags used for better organize or classify information
    metadata:
        Extra information that could be interested to include
    """

    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreationDatasetRequest(UpdateDatasetRequest):
    """
    Fields for dataset creation

    name: str
        the  dataset name
    """

    name: str = Field(regex="^(?!-|_)[a-z0-9-_]+$")


class CopyDatasetRequest(CreationDatasetRequest):
    """
    Request body for copy dataset operation
    """

    pass


class BaseDatasetDB(CreationDatasetRequest):
    """
    Low level dataset data model

    Attributes:
    -----------
    task:
        The dataset task type. Deprecated
    owner:
        The dataset owner
    created_at:
        The dataset creation date
    last_updated:
        The last modification date
    """

    task: TaskType
    owner: str = None
    created_at: datetime = None
    last_updated: datetime = None

    @property
    def id(self) -> str:
        """The dataset id. Compounded by owner and name"""
        if self.owner:
            return f"{self.owner}.{self.name}"
        return self.name


class DatasetDB(BaseDatasetDB):
    metrics: List[DatasetMetricDB] = Field(default_factory=list)


class Dataset(BaseDatasetDB):
    """Dataset used for response output"""

    pass
