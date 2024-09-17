# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydantic import BaseModel


class DatasetProgressModel(BaseModel):
    """Dataset progress model."""

    total: int = 0
    completed: int = 0
    pending: int = 0


class RecordResponseDistributionModel(BaseModel):
    """Response distribution model."""

    submitted: int = 0
    draft: int = 0
    discarded: int = 0


class UserProgressModel(BaseModel):
    """User progress model."""

    username: str
    completed: RecordResponseDistributionModel = RecordResponseDistributionModel()
    pending: RecordResponseDistributionModel = RecordResponseDistributionModel()
