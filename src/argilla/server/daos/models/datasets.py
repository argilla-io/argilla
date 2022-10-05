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

from datetime import datetime
from typing import Any, Dict, Optional, TypeVar

from pydantic import BaseModel, Field

from argilla._constants import DATASET_NAME_REGEX_PATTERN
from argilla.server.commons.models import TaskType


class BaseDatasetDB(BaseModel):
    name: str = Field(regex=DATASET_NAME_REGEX_PATTERN)
    task: TaskType
    owner: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = None
    created_by: str = Field(
        None, description="The argilla user that created the dataset"
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

    def dict(self, *args, **kwargs) -> "DictStrAny":
        """
        Extends base component dict extending object properties
        and user defined extended fields
        """
        return {
            **super().dict(*args, **kwargs),
            "id": self.id,
        }


class BaseDatasetSettingsDB(BaseModel):
    pass


DatasetDB = TypeVar("DatasetDB", bound=BaseDatasetDB)
DatasetSettingsDB = TypeVar("DatasetSettingsDB", bound=BaseDatasetSettingsDB)
