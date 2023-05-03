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
from typing import Any, Dict

from pydantic import BaseModel, Field


class BaseDatasetModel(BaseModel):
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    name: str = Field(regex="^(?!-|_)[a-zA-Z0-9-_ ]+$")


class FeedbackDataset(BaseDatasetModel):
    id: str
    guidelines: str = None
    status: str = None
    workspace_id: str = None
    created_at: datetime = None
    last_updated: datetime = None
