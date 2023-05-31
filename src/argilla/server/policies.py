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

from sqlalchemy.orm.session import Session

from argilla.server.contexts import accounts
from argilla.server.errors import ForbiddenOperationError
from argilla.server.models import (
    Dataset,
    Record,
    Response,
    User,
    UserRole,
    Workspace,
    WorkspaceUser,
)

PolicyAction = Callable[[User], bool]


class WorkspaceUserPolicy:
    @classmethod
    def list(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def create(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, workspace_user: WorkspaceUser) -> PolicyAction:
        return lambda actor: actor.role == UserRole.admin


class WorkspacePolicy:
    @classmethod
    def list(cls, actor: User) -> bool:
        return True

    @classmethod
    def create(cls, actor: User) -> bool:
        # TODO: Once we receive ORM User models instead of Pydantic schema for current_user we can
        # change role checks to use `actor.is_admin` or `actor.is_annotator`
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, workspace: Workspace) -> PolicyAction:
        return lambda actor: actor.role == UserRole.admin


class WorkspacePolicyV1:
    @classmethod
    def get(cls, workspace: Workspace) -> PolicyAction:
        return lambda actor: (
            actor.is_admin
            or bool(
                accounts.get_workspace_user_by_workspace_id_and_user_id(
                    Session.object_session(actor),
                    workspace.id,
                    actor.id,
                )
            )
        )


class UserPolicy:
    @classmethod
    def list(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def create(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, user: User) -> PolicyAction:
        return lambda actor: actor.role == UserRole.admin


class DatasetPolicy:
    @classmethod
    def list(cls, user: User) -> bool:
        return True

    @classmethod
    def get(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_admin or dataset.workspace in [ws.name for ws in actor.workspaces]

    @classmethod
    def create(cls, user: User) -> bool:
        return user.is_admin

    @classmethod
    def update(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)
        return lambda actor: actor.is_admin or is_get_allowed(actor)

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)
        return lambda actor: actor.is_admin or (is_get_allowed(actor) and actor.username == dataset.created_by)

    @classmethod
    def open(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)
        return lambda actor: actor.is_admin or (is_get_allowed(actor) and actor.username == dataset.created_by)

    @classmethod
    def close(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)
        return lambda actor: actor.is_admin or (is_get_allowed(actor) and actor.username == dataset.created_by)

    @classmethod
    def copy(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)
        return lambda actor: actor.is_admin or is_get_allowed(actor) and cls.create(actor)


class DatasetPolicyV1:
    @classmethod
    def list(cls, actor: User) -> bool:
        return True

    @classmethod
    def get(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: (
            actor.is_admin
            or bool(
                accounts.get_workspace_user_by_workspace_id_and_user_id(
                    Session.object_session(actor),
                    dataset.workspace_id,
                    actor.id,
                )
            )
        )

    @classmethod
    def list_dataset_records_will_all_responses(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_admin

    @classmethod
    def create(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    def create_field(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    def create_question(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    def create_records(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    def publish(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    def delete(cls, actor: User) -> bool:
        return actor.is_admin


class FieldPolicyV1:
    @classmethod
    def delete(cls, actor: User) -> bool:
        return actor.is_admin


class QuestionPolicyV1:
    @classmethod
    def delete(cls, actor: User) -> bool:
        return actor.is_admin


class RecordPolicyV1:
    @classmethod
    def create_response(cls, record: Record) -> PolicyAction:
        return lambda actor: (
            actor.is_admin
            or bool(
                accounts.get_workspace_user_by_workspace_id_and_user_id(
                    Session.object_session(actor),
                    record.dataset.workspace_id,
                    actor.id,
                )
            )
        )


class ResponsePolicyV1:
    @classmethod
    def update(cls, response: Response) -> PolicyAction:
        return lambda actor: actor.is_admin or actor.id == response.user_id

    @classmethod
    def delete(cls, response: Response) -> PolicyAction:
        return lambda actor: actor.is_admin or actor.id == response.user_id


class DatasetSettingsPolicy:
    @classmethod
    def list(cls, dataset: Dataset) -> PolicyAction:
        return DatasetPolicy.get(dataset)

    @classmethod
    def save(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_admin

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        return lambda actor: actor.is_admin


def authorize(actor: User, policy_action: PolicyAction) -> None:
    if not is_authorized(actor, policy_action):
        raise ForbiddenOperationError()


def is_authorized(actor: User, policy_action: PolicyAction) -> bool:
    return policy_action(actor)
