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

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from argilla.pydantic_v1 import BaseModel, Field


class TaskType(str, Enum):
    text_classification = "TextClassification"
    token_classification = "TokenClassification"
    text2text = "Text2Text"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, please select one of {list(cls._value2member_map_.keys())}"
        )


class BaseDatasetModel(BaseModel):
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    name: str = Field(regex="^(?!-|_)[a-z0-9-_]+$")


class Dataset(BaseDatasetModel):
    id: str
    task: TaskType
    workspace: str = None
    created_at: datetime = None
    last_updated: datetime = None


class CopyDatasetRequest(BaseDatasetModel):
    target_workspace: Optional[str] = None
