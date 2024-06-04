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

from argilla_server.api.policies.v1.commons import PolicyAction, is_authorized
from argilla_server.api.policies.v1.metadata_property_policy import MetadataPropertyPolicy
from argilla_server.models import Record, User


class RecordPolicy:
    @classmethod
    def get(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await actor.is_member(record.dataset.workspace_id)

        return is_allowed

    @classmethod
    def update(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(record.dataset.workspace_id))

        return is_allowed

    @classmethod
    def delete(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(record.dataset.workspace_id))

        return is_allowed

    @classmethod
    def create_response(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await actor.is_member(record.dataset.workspace_id)

        return is_allowed

    @classmethod
    def get_suggestions(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await actor.is_member(record.dataset.workspace_id)

        return is_allowed

    @classmethod
    def create_suggestion(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(record.dataset.workspace_id))

        return is_allowed

    @classmethod
    def delete_suggestions(cls, record: Record) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(record.dataset.workspace_id))

        return is_allowed

    @classmethod
    def get_metadata(cls, record: Record, metadata_name: str):
        async def is_allowed(actor: User) -> bool:
            if actor.is_owner:
                return True

            metadata_property = record.dataset.metadata_property_by_name(metadata_name)
            if metadata_property:
                return await is_authorized(actor, MetadataPropertyPolicy.get(metadata_property))

            return actor.is_admin and await actor.is_member(record.dataset.workspace_id)

        return is_allowed
