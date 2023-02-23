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

from argilla.server.contexts import accounts
from argilla.server.security.model import WorkspaceCreate
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_list_workspaces(client: TestClient, api_key_header: dict, db: Session):
    accounts.create_workspace(db, WorkspaceCreate(name="workspace-a"))
    accounts.create_workspace(db, WorkspaceCreate(name="workspace-b"))

    response = client.get("/api/workspaces", headers=api_key_header)

    workspaces = response.json()

    assert response.status_code == 200
    assert list(map(lambda ws: ws["name"], workspaces)) == ["workspace-a", "workspace-b"]
