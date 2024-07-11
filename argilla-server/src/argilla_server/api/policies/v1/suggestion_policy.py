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

from argilla_server.api.policies.v1.commons import PolicyAction
from argilla_server.models import Suggestion, User


class SuggestionPolicy:
    @classmethod
    def delete(cls, suggestion: Suggestion) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or (actor.is_admin and await actor.is_member(suggestion.record.dataset.workspace_id))

        return is_allowed
