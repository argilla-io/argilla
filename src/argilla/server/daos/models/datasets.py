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
from typing import Any, Dict, Optional, TypeVar, Union

from pydantic import BaseModel, Field, root_validator

from argilla._constants import ES_INDEX_REGEX_PATTERN
from argilla.server.commons.models import TaskType


class BaseDatasetDB(BaseModel):
    name: str = Field(regex=ES_INDEX_REGEX_PATTERN)
    task: TaskType
    owner: Optional[str] = Field(description="Deprecated. Use `workspace` instead. Will be removed in v1.5.0")
    workspace: Optional[str]

    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = None
    created_by: str = Field(
        None,
        description="The argilla user that created the dataset",
    )
    last_updated: datetime = None

    class Config:
        validate_assignment = True

    @root_validator(pre=True)
    def set_defaults(cls, values):
        workspace = values.get("workspace") or values.get("owner")

        cls._check_workspace(workspace)

        values["workspace"] = workspace
        values["owner"] = workspace

        return values

    @classmethod
    def _check_workspace(cls, workspace: str):
        if not workspace:
            raise ValueError("Missing workspace")

    @classmethod
    def build_dataset_id(cls, name: str, workspace: str) -> str:
        """Build a dataset id for a given name and workspace"""
        cls._check_workspace(workspace)
        return f"{workspace}.{name}"

    @property
    def id(self) -> str:
        """The dataset id. Compounded by workspace and name"""
        return self.build_dataset_id(self.name, self.workspace)

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Extends base component dict extending object properties
        and user defined extended fields
        """
        return {
            **super().dict(*args, **kwargs),
            "id": self.id,
        }


class EmbeddingsConfig(BaseModel):
    dim: int = Field(
        description="The number of dimensions for the named vectors",
    )


class BaseDatasetSettingsDB(BaseModel):
    vectors: Optional[Dict[str, Union[int, EmbeddingsConfig]]] = Field(
        default=None,
        description="The vectors configuration",
    )


DatasetDB = TypeVar("DatasetDB", bound=BaseDatasetDB)
DatasetSettingsDB = TypeVar("DatasetSettingsDB", bound=BaseDatasetSettingsDB)
