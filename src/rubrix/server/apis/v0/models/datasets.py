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
from typing import Any, ClassVar, Dict, Optional

from pydantic import BaseModel, Field

from rubrix._constants import DATASET_NAME_REGEX_PATTERN
from rubrix.server.apis.v0.models.commons.model import TaskType


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
    name: str = Field(regex=DATASET_NAME_REGEX_PATTERN, description="The dataset name")


class DatasetCreate(CreationDatasetRequest):
    task: TaskType = Field(description="The dataset task")


class CopyDatasetRequest(CreationDatasetRequest):
    """
    Request body for copy dataset operation
    """

    target_workspace: Optional[str] = None


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
    owner: Optional[str] = None
    created_at: datetime = None
    created_by: str = Field(
        None, description="The Rubrix user that created the dataset"
    )
    last_updated: datetime = None

    @classmethod
    def build_dataset_id(cls, name: str, owner: Optional[str] = None) -> str:
        """Build a dataset id for a given name and owner"""
        if owner:
            return f"{owner}.{name}"
        return name

    @property
    def id(self) -> str:
        """The dataset id. Compounded by owner and name"""
        return self.build_dataset_id(self.name, self.owner)


# TODO: Move this class to the services layer
class DatasetDB(BaseDatasetDB):
    pass


class Dataset(BaseDatasetDB):
    """Dataset used for response output"""

    pass
