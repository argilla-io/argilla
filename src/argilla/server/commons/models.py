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
import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator


class TaskStatus(str, Enum):
    default = "Default"
    edited = "Edited"  # TODO: DEPRECATE
    discarded = "Discarded"
    validated = "Validated"


class TaskType(str, Enum):

    text_classification = "TextClassification"
    token_classification = "TokenClassification"
    text2text = "Text2Text"
    multi_task_text_token_classification = "MultitaskTextTokenClassification"


class PredictionStatus(str, Enum):
    OK = "ok"
    KO = "ko"


class BaseLabelingRule(BaseModel):

    __SANITIZE_REGEX__ = re.compile(r"(\w|[0-9]|_|-|\.)+")

    name: Optional[str] = Field(
        default=None,
        description="The rule name. If not provided will be computed from query",
    )
    query: str = Field(description="The rule query")

    author: Optional[str] = Field(
        default=None,
        description="User who created the rule",
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Rule creation timestamp",
    )

    description: Optional[str] = Field(
        None,
        description="A brief description of the rule",
    )

    @validator("query")
    def strip_query(cls, query: str) -> str:
        """Remove blank spaces for query"""
        return query.strip()

    @root_validator
    def compute_id(cls, values):
        id_ = values.get("name")
        query = values["query"]

        if not id_:
            values["name"] = cls.__sanitize_query__(query)

        return values

    @classmethod
    def __sanitize_query__(cls, query: str) -> str:
        return "_".join(cls.__SANITIZE_REGEX__.findall(query))
