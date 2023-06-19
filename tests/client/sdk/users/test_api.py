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

import pytest
from argilla.client.client import Argilla
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.users.api import whoami
from argilla.client.sdk.users.models import UserModel
from httpx import ConnectError


def test_whoami(api: Argilla):
    user = whoami(client=api.http_client.httpx).parsed
    assert isinstance(user, UserModel)


def test_whoami_with_connection_error():
    with pytest.raises(ConnectError):
        whoami(AuthenticatedClient(base_url="http://localhost:6900", token="wrong-apikey").httpx)
