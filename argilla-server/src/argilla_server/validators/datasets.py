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

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import Dataset, Field, Question, Workspace
from argilla_server.errors.future import (
    NotUniqueError,
    UnprocessableEntityError,
    UpdateDistributionWithExistingResponsesError,
)


class DatasetCreateValidator:
    @classmethod
    async def validate(cls, db: AsyncSession, dataset: Dataset) -> None:
        await cls._validate_workspace_is_present(db, dataset.workspace_id)
        await cls._validate_name_is_not_duplicated(db, dataset.name, dataset.workspace_id)

    @classmethod
    async def _validate_workspace_is_present(cls, db: AsyncSession, workspace_id: UUID) -> None:
        if await Workspace.get(db, workspace_id) is None:
            raise UnprocessableEntityError(f"Workspace with id `{workspace_id}` not found")

    @classmethod
    async def _validate_name_is_not_duplicated(cls, db: AsyncSession, name: str, workspace_id: UUID) -> None:
        if await Dataset.get_by(db, name=name, workspace_id=workspace_id):
            raise NotUniqueError(f"Dataset with name `{name}` already exists for workspace with id `{workspace_id}`")


class DatasetPublishValidator:
    @classmethod
    async def validate(cls, db: AsyncSession, dataset: Dataset) -> None:
        await cls._validate_has_not_been_published_yet(db, dataset)
        await cls._validate_has_at_least_one_field(db, dataset)
        await cls._validate_has_at_least_one_required_question(db, dataset)

    @classmethod
    async def _validate_has_not_been_published_yet(cls, db: AsyncSession, dataset: Dataset) -> None:
        if dataset.is_ready:
            raise UnprocessableEntityError("Dataset has already been published")

    @classmethod
    async def _validate_has_at_least_one_field(cls, db: AsyncSession, dataset: Dataset) -> None:
        if await Field.count_by(db, dataset_id=dataset.id) == 0:
            raise UnprocessableEntityError("Dataset cannot be published without fields")

    @classmethod
    async def _validate_has_at_least_one_required_question(cls, db: AsyncSession, dataset: Dataset) -> None:
        if await Question.count_by(db, dataset_id=dataset.id, required=True) == 0:
            raise UnprocessableEntityError("Dataset cannot be published without required questions")


class DatasetUpdateValidator:
    @classmethod
    async def validate(cls, db: AsyncSession, dataset: Dataset, dataset_attrs: dict) -> None:
        pass
