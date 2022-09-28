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

from argilla.client.sdk.users.models import User
from argilla.server.security.model import User as ServerUser


def test_users_schema(helpers):
    client_schema = User.schema()
    server_schema = ServerUser.schema()

    for clean_method in [helpers.remove_description, helpers.remove_pattern]:
        client_schema = clean_method(client_schema)
        server_schema = clean_method(server_schema)

    assert client_schema == server_schema
