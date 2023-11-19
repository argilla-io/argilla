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

from typing import Awaitable, Callable, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import async_object_session

from argilla.server.contexts import accounts
from argilla.server.daos.models.datasets import DatasetDB
from argilla.server.errors import ForbiddenOperationError
from argilla.server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    Record,
    Response,
    Suggestion,
    User,
    UserRole,
    VectorSettings,
    Workspace,
    WorkspaceUser,
)

PolicyAction = Callable[[User], Awaitable[bool]]


async def _exists_workspace_user_by_user_and_workspace_id(user: User, workspace_id: UUID) -> bool:
    db = async_object_session(user)
    workspace = await accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace_id, user.id)
    return workspace is not None


async def _exists_workspace_user_by_user_and_workspace_name(user: User, workspace_name: str) -> bool:
    db = async_object_session(user)
    workspace = await accounts.get_workspace_by_name(db, workspace_name)
    if workspace is None:
        return False
    return await accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace.id, user.id) is not None


class WorkspaceUserPolicy:
    @classmethod
    def list(cls, workspace_id: UUID) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, workspace_id)
            )

        return is_allowed

    @classmethod
    async def create(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    def delete(cls, workspace_user: WorkspaceUser) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.role == UserRole.owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, workspace_user.workspace_id)
            )

        return is_allowed


class WorkspacePolicy:
    @classmethod
    async def list(cls, actor: User) -> bool:
        return True

    @classmethod
    async def create(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    def delete(cls, workspace: Workspace) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner

        return is_allowed


class WorkspacePolicyV1:
    @classmethod
    def get(cls, workspace_id: UUID) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_id(actor, workspace_id)

        return is_allowed

    @classmethod
    async def delete(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    async def list_workspaces_me(cls, actor: User) -> bool:
        return True


class UserPolicy:
    @classmethod
    async def list(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    async def create(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    def delete(cls, user: User) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner

        return is_allowed


class UserPolicyV1:
    @classmethod
    async def list_workspaces(cls, actor: User) -> bool:
        return actor.is_owner


class DatasetPolicy:
    @classmethod
    async def list(cls, user: User) -> bool:
        return True

    @classmethod
    def get(cls, dataset: DatasetDB) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)

        return is_allowed

    @classmethod
    def create(cls, workspace_name: str) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_name(actor, workspace_name)
            )

        return is_allowed

    @classmethod
    def update(cls, dataset: DatasetDB) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)

        return is_allowed

    @classmethod
    def delete(cls, dataset: DatasetDB) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
            )

        return is_allowed

    @classmethod
    def open(cls, dataset: DatasetDB) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
            )

        return is_allowed

    @classmethod
    def close(cls, dataset: DatasetDB) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
            )

        return is_allowed

    @classmethod
    def copy(cls, dataset: DatasetDB, target_workspace: Workspace) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, target_workspace.id)
                and await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
            )

        return is_allowed

    @classmethod
    def delete_records(cls, dataset: DatasetDB) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
            )

        return is_allowed


class DatasetPolicyV1:
    @classmethod
    def list(cls, workspace_id: Optional[UUID] = None) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            if actor.is_owner or workspace_id is None:
                return True

            return await _exists_workspace_user_by_user_and_workspace_id(actor, workspace_id)

        return is_allowed

    @classmethod
    def list_records_with_all_responses(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def get(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)

        return is_allowed

    @classmethod
    def create(cls, workspace_id: UUID) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, workspace_id)
            )

        return is_allowed

    @classmethod
    def create_field(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def create_question(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def create_metadata_property(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def create_vectors(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def create_vector_settings(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def create_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def update_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def search_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)

        return is_allowed

    @classmethod
    def search_records_with_all_responses(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def publish(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def update(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
            )

        return is_allowed


class FieldPolicyV1:
    @classmethod
    def update(cls, field: Field) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, field.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete(cls, field: Field) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, field.dataset.workspace_id)
            )

        return is_allowed


class QuestionPolicyV1:
    @classmethod
    def update(cls, question: Question) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, question.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete(cls, question: Question) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, question.dataset.workspace_id)
            )

        return is_allowed


class VectorSettingsPolicyV1:
    @classmethod
    def update(cls, vector_settings: VectorSettings) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, vector_settings.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete(cls, vector_settings: VectorSettings) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, vector_settings.dataset.workspace_id)
            )

        return is_allowed


class MetadataPropertyPolicyV1:
    @classmethod
    def get(cls, metadata_property: MetadataProperty) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.role in metadata_property.allowed_roles
                and await _exists_workspace_user_by_user_and_workspace_id(actor, metadata_property.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def update(cls, metadata_property: MetadataProperty) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, metadata_property.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete(cls, metadata_property: MetadataProperty) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, metadata_property.dataset.workspace_id)
            )

        return is_allowed


class RecordPolicyV1:
    @classmethod
    def get(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_id(
                actor, record.dataset.workspace_id
            )

        return is_allowed

    @classmethod
    def update(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, record.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, record.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def create_response(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_id(
                actor, record.dataset.workspace_id
            )

        return is_allowed

    @classmethod
    def get_suggestions(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await _exists_workspace_user_by_user_and_workspace_id(
                actor, record.dataset.workspace_id
            )

        return is_allowed

    @classmethod
    def create_suggestion(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, record.dataset.workspace_id)
            )

        return is_allowed

    @classmethod
    def delete_suggestions(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, record.dataset.workspace_id)
            )

        return is_allowed


class ResponsePolicyV1:
    @classmethod
    def update(cls, response: Response) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return (
                actor.is_owner
                or actor.id == response.user_id
                or (
                    actor.is_admin
                    and await _exists_workspace_user_by_user_and_workspace_id(
                        actor, response.record.dataset.workspace_id
                    )
                )
            )

        return is_allowed

    @classmethod
    def delete(cls, response: Response) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return (
                actor.is_owner
                or actor.id == response.user_id
                or (
                    actor.is_admin
                    and await _exists_workspace_user_by_user_and_workspace_id(
                        actor, response.record.dataset.workspace_id
                    )
                )
            )

        return is_allowed


class SuggestionPolicyV1:
    @classmethod
    def delete(cls, suggestion: Suggestion) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin
                and await _exists_workspace_user_by_user_and_workspace_id(actor, suggestion.record.dataset.workspace_id)
            )

        return is_allowed


class DatasetSettingsPolicy:
    @classmethod
    def list(cls, dataset: DatasetDB) -> PolicyAction:
        return DatasetPolicy.get(dataset)

    @classmethod
    def save(cls, dataset: DatasetDB) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
            )

        return is_allowed

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (
                actor.is_admin and await _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
            )

        return is_allowed


async def authorize(actor: User, policy_action: PolicyAction) -> None:
    if not await is_authorized(actor, policy_action):
        raise ForbiddenOperationError()


async def is_authorized(actor: User, policy_action: PolicyAction) -> bool:
    return await policy_action(actor)
