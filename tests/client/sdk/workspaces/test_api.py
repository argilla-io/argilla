#  coding=utf-8
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
from argilla._constants import DEFAULT_API_KEY
from argilla.client.client import Argilla
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.workspaces.api import list_workspaces
from argilla.client.sdk.workspaces.models import WorkspaceModel


def test_list_workspaces(api: Argilla) -> None:
    response = list_workspaces(client=api.http_client.httpx)

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], WorkspaceModel)
