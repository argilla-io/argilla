# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, List, Optional
from uuid import UUID

import httpx

from argilla._api._base import ResourceAPI
from argilla._exceptions._api import api_error_handler
from argilla._models._workspace import WorkspaceModel

__all__ = ["WorkspacesAPI"]


class WorkspacesAPI(ResourceAPI[WorkspaceModel]):
    http_client: httpx.Client
    url_stub = "/api/v1/workspaces"

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(self, workspace: WorkspaceModel) -> WorkspaceModel:
        # TODO: Unify API endpoint
        response = self.http_client.post(url="/api/v1/workspaces", json={"name": workspace.name})
        response.raise_for_status()
        response_json = response.json()
        workspace = self._model_from_json(json_workspace=response_json)
        self._log_message(message=f"Created workspace {workspace.name}")
        return workspace

    @api_error_handler
    def get(self, workspace_id: UUID) -> WorkspaceModel:
        response = self.http_client.get(url=f"{self.url_stub}/{workspace_id}")
        response.raise_for_status()
        response_json = response.json()
        workspace = self._model_from_json(json_workspace=response_json)
        return workspace

    @api_error_handler
    def delete(self, workspace_id: UUID) -> None:
        response = self.http_client.delete(url=f"{self.url_stub}/{workspace_id}")
        response.raise_for_status()

    def exists(self, workspace_id: UUID) -> bool:
        response = self.http_client.get(url=f"{self.url_stub}/{workspace_id}")
        return response.status_code == 200

    ####################
    # Utility methods #
    ####################

    @api_error_handler
    def list(self) -> List[WorkspaceModel]:
        response = self.http_client.get(url="/api/v1/me/workspaces")
        response.raise_for_status()
        response_json = response.json()
        workspaces = self._model_from_jsons(json_workspaces=response_json["items"])
        self._log_message(message=f"Got {len(workspaces)} workspaces")
        return workspaces

    @api_error_handler
    def list_by_user_id(self, user_id: UUID) -> List[WorkspaceModel]:
        response = self.http_client.get(f"/api/v1/users/{user_id}/workspaces")
        response.raise_for_status()
        response_json = response.json()
        workspaces = self._model_from_jsons(json_workspaces=response_json["items"])
        self._log_message(message=f"Got {len(workspaces)} workspaces")
        return workspaces

    @api_error_handler
    def list_current_user_workspaces(self) -> List[WorkspaceModel]:
        response = self.http_client.get(url="/api/v1/me/workspaces")
        response.raise_for_status()
        response_json = response.json()
        workspaces = self._model_from_jsons(json_workspaces=response_json["items"])
        self._log_message(message=f"Got {len(workspaces)} workspaces")
        return workspaces

    @api_error_handler
    def get_by_name(self, name: str) -> Optional[WorkspaceModel]:
        for workspace in self.list():
            if workspace.name == name:
                self._log_message(message=f"Got workspace {workspace.name}")
                return workspace

    @api_error_handler
    def add_user(self, workspace_id: UUID, user_id: UUID) -> None:
        # TODO: This method is already defined in UsersAPI and should be removed from here
        response = self.http_client.post(f"{self.url_stub}/{workspace_id}/users/{user_id}")
        response.raise_for_status()
        self._log_message(message=f"Added user {user_id} to workspace {workspace_id}")

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, json_workspace: Dict) -> WorkspaceModel:
        return WorkspaceModel(
            id=UUID(json_workspace["id"]),
            name=json_workspace["name"],
            inserted_at=self._date_from_iso_format(date=json_workspace["inserted_at"]),
            updated_at=self._date_from_iso_format(date=json_workspace["updated_at"]),
        )

    def _model_from_jsons(self, json_workspaces: List[Dict]) -> List[WorkspaceModel]:
        return list(map(self._model_from_json, json_workspaces))
