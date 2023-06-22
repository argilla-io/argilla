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

from typing import Callable
from uuid import UUID

from sqlalchemy.orm.session import Session

from argilla.server.contexts import accounts
from argilla.server.daos.models.datasets import DatasetDB
from argilla.server.errors import ForbiddenOperationError
from argilla.server.models import (
    Dataset,
    Field,
    Question,
    Record,
    Response,
    User,
    UserRole,
    Workspace,
    WorkspaceUser,
)

PolicyAction = Callable[[User], bool]


def _exists_workspace_user_by_user_and_workspace_id(user: User, workspace_id: UUID) -> bool:
    return (
        accounts.get_workspace_user_by_workspace_id_and_user_id(Session.object_session(user), workspace_id, user.id)
        is not None
    )


def _exists_workspace_user_by_user_and_workspace_name(user: User, workspace_name: str) -> bool:
    db = Session.object_session(user)

    workspace = accounts.get_workspace_by_name(db, workspace_name)
    if workspace is None:
        return False
    return accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace.id, user.id) is not None


class WorkspaceUserPolicy:
    @classmethod
    def list(cls, workspace_id: UUID) -> PolicyAction:
        return lambda actor: actor.role == UserRole.owner or (
            actor.role == UserRole.admin and _exists_workspace_user_by_user_and_workspace_id(actor, workspace_id)
        )

    @classmethod
    def create(cls, actor: User) -> bool:
        return actor.role == UserRole.owner

    @classmethod
    def delete(cls, workspace_user: WorkspaceUser) -> PolicyAction:
        return lambda actor: actor.role == UserRole.owner or (
            actor.role == UserRole.admin
            and _exists_workspace_user_by_user_and_workspace_id(actor, workspace_user.workspace_id)
        )


class WorkspacePolicy:
    @classmethod
    def list(cls, actor: User) -> bool:
        return True

    @classmethod
    def create(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    def delete(cls, workspace: Workspace) -> PolicyAction:
        return lambda actor: actor.role == UserRole.owner


class WorkspacePolicyV1:
    @classmethod
    def get(cls, workspace_id: UUID) -> PolicyAction:
        return lambda actor: actor.is_owner or _exists_workspace_user_by_user_and_workspace_id(actor, workspace_id)


class UserPolicy:
    @classmethod
    def list(cls, actor: User) -> bool:
        return actor.role == UserRole.owner

    @classmethod
    def create(cls, actor: User) -> bool:
        return actor.role == UserRole.owner

    @classmethod
    def delete(cls, user: User) -> PolicyAction:
        return lambda actor: actor.role == UserRole.owner


class DatasetPolicy:
    @classmethod
    def list(cls, user: User) -> bool:
        return True

    @classmethod
    def get(cls, dataset: DatasetDB) -> PolicyAction:
        return lambda actor: actor.is_owner or _exists_workspace_user_by_user_and_workspace_name(
            actor, dataset.workspace
        )

    @classmethod
    def create(cls, workspace_name: str) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_name(actor, workspace_name)
        )

    @classmethod
    def update(cls, dataset: DatasetDB) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )

    @classmethod
    def delete(cls, dataset: DatasetDB) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )

    @classmethod
    def open(cls, dataset: DatasetDB) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )

    @classmethod
    def close(cls, dataset: DatasetDB) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )

    @classmethod
    def copy(cls, dataset: DatasetDB, target_workspace: Workspace) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin
            and _exists_workspace_user_by_user_and_workspace_id(actor, target_workspace.id)
            and _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )

    @classmethod
    def delete_records(cls, dataset: DatasetDB) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )


class DatasetPolicyV1:
    @classmethod
    def list(cls, actor: User) -> bool:
        return True

    @classmethod
    def get(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: (
            actor.is_owner or _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )

    @classmethod
    def list_dataset_records_will_all_responses(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )

    @classmethod
    def create(cls, workspace_id: UUID) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, workspace_id)
        )

    @classmethod
    def create_field(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )

    @classmethod
    def create_question(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )

    @classmethod
    def create_records(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )

    @classmethod
    def search_records(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: (
            actor.is_owner or _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )

    @classmethod
    def publish(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, dataset.workspace_id)
        )


class FieldPolicyV1:
    @classmethod
    def delete(cls, field: Field) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, field.dataset.workspace_id)
        )


class QuestionPolicyV1:
    @classmethod
    def delete(cls, question: Question) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_id(actor, question.dataset.workspace_id)
        )


class RecordPolicyV1:
    @classmethod
    def create_response(cls, record: Record) -> PolicyAction:
        return lambda actor: (
            actor.is_owner or _exists_workspace_user_by_user_and_workspace_id(actor, record.dataset.workspace_id)
        )


class ResponsePolicyV1:
    @classmethod
    def update(cls, response: Response) -> PolicyAction:
        return (
            lambda actor: actor.is_owner
            or actor.id == response.user_id
            or (
                actor.is_admin
                and _exists_workspace_user_by_user_and_workspace_id(actor, response.record.dataset.workspace_id)
            )
        )

    @classmethod
    def delete(cls, response: Response) -> PolicyAction:
        return (
            lambda actor: actor.is_owner
            or actor.id == response.user_id
            or (
                actor.is_admin
                and _exists_workspace_user_by_user_and_workspace_id(actor, response.record.dataset.workspace_id)
            )
        )


class DatasetSettingsPolicy:
    @classmethod
    def list(cls, dataset: DatasetDB) -> PolicyAction:
        return DatasetPolicy.get(dataset)

    @classmethod
    def save(cls, dataset: DatasetDB) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_owner or (
            actor.is_admin and _exists_workspace_user_by_user_and_workspace_name(actor, dataset.workspace)
        )


def authorize(actor: User, policy_action: PolicyAction) -> None:
    if not is_authorized(actor, policy_action):
        raise ForbiddenOperationError()


def is_authorized(actor: User, policy_action: PolicyAction) -> bool:
    return policy_action(actor)
