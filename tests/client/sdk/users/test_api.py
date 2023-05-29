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

from argilla._constants import DEFAULT_API_KEY
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.users.api import whoami
from argilla.client.sdk.users.models import User


def test_whoami(monkeypatch, mocked_client) -> None:
    httpx_client = AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY)
    monkeypatch.setattr(httpx_client, "get", mocked_client.get)
    response = whoami(client=httpx_client)
    assert response.status_code == 200
    assert isinstance(response.parsed, User)
