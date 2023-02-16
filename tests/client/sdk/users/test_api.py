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
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.errors import BaseClientError, UnauthorizedApiError
from argilla.client.sdk.users.api import whoami
from argilla.client.sdk.users.models import User


def test_whoami(mocked_client, sdk_client):
    user = whoami(client=sdk_client)
    assert isinstance(user, User)


def test_whoami_with_auth_error(monkeypatch, mocked_client):
    with pytest.raises(UnauthorizedApiError):
        sdk_client = AuthenticatedClient(base_url="http://localhost:6900", token="wrong-apikey")
        monkeypatch.setattr(sdk_client, "__httpx__", mocked_client)
        whoami(sdk_client)


def test_whoami_with_connection_error():
    with pytest.raises(BaseClientError):
        whoami(AuthenticatedClient(base_url="http://localhost:6900", token="wrong-apikey"))
