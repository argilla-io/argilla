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

from typing import Awaitable, Callable

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

PolicyAction = Callable[[User], Awaitable[bool]]


class WorkspaceUserPolicy:
    @classmethod
    async def list(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    async def create(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    async def delete(cls, workspace_user: WorkspaceUser) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.role == UserRole.admin

        return is_allowed


class WorkspacePolicy:
    @classmethod
    async def list(cls, actor: User) -> bool:
        return True

    @classmethod
    async def create(cls, actor: User) -> bool:
        # TODO: Once we receive ORM User models instead of Pydantic schema for current_user we can
        # change role checks to use `actor.is_admin` or `actor.is_annotator`
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, workspace: Workspace) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.role == UserRole.admin

        return is_allowed


class WorkspacePolicyV1:
    @classmethod
    def get(cls, workspace: Workspace) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or bool(
                accounts.get_workspace_user_by_workspace_id_and_user_id(
                    Session.object_session(actor),
                    workspace.id,
                    actor.id,
                )
            )

        return is_allowed


class UserPolicy:
    @classmethod
    async def list(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    async def create(cls, actor: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, user: User) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.role == UserRole.admin

        return is_allowed


class DatasetPolicy:
    @classmethod
    async def list(cls, user: User) -> bool:
        return True

    @classmethod
    def get(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or dataset.workspace in [ws.name for ws in actor.workspaces]

        return is_allowed

    @classmethod
    async def create(cls, user: User) -> bool:
        return user.is_admin

    @classmethod
    def update(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)

        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or await is_get_allowed(actor)

        return is_allowed

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)

        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or (await is_get_allowed(actor) and actor.username == dataset.created_by)

        return is_allowed

    @classmethod
    def open(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)

        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or (await is_get_allowed(actor) and actor.username == dataset.created_by)

        return is_allowed

    @classmethod
    def close(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)

        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or (await is_get_allowed(actor) and actor.username == dataset.created_by)

        return is_allowed

    @classmethod
    def copy(cls, dataset: Dataset) -> PolicyAction:
        is_get_allowed = cls.get(dataset)

        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or (await is_get_allowed(actor) and actor.username == dataset.created_by)

        return is_allowed


class DatasetPolicyV1:
    @classmethod
    async def list(cls, actor: User) -> bool:
        return True

    @classmethod
    def get(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or bool(
                await accounts.get_workspace_user_by_workspace_id_and_user_id(
                    Session.object_session(actor),
                    dataset.workspace_id,
                    actor.id,
                )
            )

        return is_allowed

    @classmethod
    def list_dataset_records_will_all_responses(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin

        return is_allowed

    @classmethod
    async def create(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    async def create_field(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    async def create_question(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    async def create_records(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    def search_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or bool(
                accounts.get_workspace_user_by_workspace_id_and_user_id(
                    Session.object_session(actor),
                    dataset.workspace_id,
                    actor.id,
                )
            )

        return is_allowed

    @classmethod
    async def publish(cls, actor: User) -> bool:
        return actor.is_admin

    @classmethod
    async def delete(cls, actor: User) -> bool:
        return actor.is_admin


class FieldPolicyV1:
    @classmethod
    async def delete(cls, actor: User) -> bool:
        return actor.is_admin


class QuestionPolicyV1:
    @classmethod
    async def delete(cls, actor: User) -> bool:
        return actor.is_admin


class RecordPolicyV1:
    @classmethod
    def create_response(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or bool(
                accounts.get_workspace_user_by_workspace_id_and_user_id(
                    Session.object_session(actor),
                    record.dataset.workspace_id,
                    actor.id,
                )
            )

        return is_allowed


class ResponsePolicyV1:
    @classmethod
    def update(cls, response: Response) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or actor.id == response.user_id

        return is_allowed

    @classmethod
    def delete(cls, response: Response) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin or actor.id == response.user_id

        return is_allowed


class DatasetSettingsPolicy:
    @classmethod
    async def list(cls, dataset: Dataset) -> PolicyAction:
        return DatasetPolicy.get(dataset)

    @classmethod
    def save(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin

        return is_allowed

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_admin

        return is_allowed


async def authorize(actor: User, policy_action: PolicyAction) -> None:
    if not await is_authorized(actor, policy_action):
        raise ForbiddenOperationError()


async def is_authorized(actor: User, policy_action: PolicyAction) -> bool:
    return await policy_action(actor)
