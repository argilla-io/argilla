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

from typing import Optional
from uuid import UUID

from argilla_server.api.policies.v1.commons import PolicyAction
from argilla_server.models import Dataset, User


class DatasetPolicy:
    @classmethod
    def list(cls, workspace_id: Optional[UUID] = None) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            if actor.is_owner or workspace_id is None:
                return True

            return await actor.is_member(workspace_id)

        return is_allowed

    @classmethod
    def list_records_with_all_responses(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def get(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await actor.is_member(dataset.workspace_id)

        return is_allowed

    @classmethod
    def create(cls, workspace_id: UUID) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(workspace_id))

        return is_allowed

    @classmethod
    def create_field(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def create_question(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def create_metadata_property(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def create_vector_settings(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def create_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def update_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def upsert_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def delete_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def search_records(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await actor.is_member(dataset.workspace_id)

        return is_allowed

    @classmethod
    def search_records_with_all_responses(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def publish(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def delete(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed

    @classmethod
    def update(cls, dataset: Dataset) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(dataset.workspace_id))

        return is_allowed
