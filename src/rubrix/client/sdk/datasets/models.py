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
from typing import Any
from typing import Dict

from pydantic import BaseModel
from pydantic import Field


class TaskType(str, Enum):
    text_classification = "TextClassification"
    token_classification = "TokenClassification"
    text2text = "Text2Text"
    multi_task_text_token_classification = "MultitaskTextTokenClassification"


class Dataset(BaseModel):
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    name: str = Field(regex="^(?!-|_)[a-z0-9-_]+$")
    task: TaskType
    owner: str = None
    created_at: datetime = None
    last_updated: datetime = None
