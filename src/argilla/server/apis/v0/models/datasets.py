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

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from argilla._constants import DATASET_NAME_REGEX_PATTERN
from argilla.server.commons.models import TaskType
from argilla.server.services.datasets import ServiceBaseDataset


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


class _BaseDatasetRequest(UpdateDatasetRequest):
    name: str = Field(regex=DATASET_NAME_REGEX_PATTERN, description="The dataset name")


class CreateDatasetRequest(_BaseDatasetRequest):
    task: TaskType = Field(description="The dataset task")


class CopyDatasetRequest(_BaseDatasetRequest):
    """
    Request body for copy dataset operation
    """

    target_workspace: Optional[str] = None


class Dataset(_BaseDatasetRequest, ServiceBaseDataset):
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
