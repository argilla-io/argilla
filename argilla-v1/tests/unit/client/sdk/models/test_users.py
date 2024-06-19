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

from argilla_server.models import UserRole as ServerUserRole
from argilla_server.schemas.v0.users import User as ServerUser
from argilla_v1.client.sdk.users.models import UserModel as ClientUser
from argilla_v1.client.sdk.users.models import UserRole as ClientUserRole

from tests.unit.client.sdk.models.conftest import Helpers


def test_users_schema(helpers: Helpers) -> None:
    assert helpers.are_compatible_api_schemas(ClientUser.schema(), ServerUser.schema())


def test_user_roles_enums() -> None:
    assert ClientUserRole.__members__.keys() == ServerUserRole.__members__.keys()
