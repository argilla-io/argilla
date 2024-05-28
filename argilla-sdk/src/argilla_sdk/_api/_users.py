# Copyright 2024-present, Argilla, Inc.
# TODO: This license is not consistent with the license used in the project.
#       Delete the inconsistent license and above line and rerun pre-commit to insert a good license.
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

from typing import List
from uuid import UUID

import httpx

from argilla_sdk._api._base import ResourceAPI
from argilla_sdk._exceptions import api_error_handler
from argilla_sdk._models._user import UserModel

__all__ = ["UsersAPI"]


class UsersAPI(ResourceAPI[UserModel]):
    """Manage users via the API"""

    http_client: httpx.Client
    url_stub = "api/v1/users"

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(self, user: UserModel) -> UserModel:
        json_body = user.model_dump()
        response = self.http_client.post("/api/users", json=json_body).raise_for_status()
        user_created = self._model_from_json(response_json=response.json())
        self.log(message=f"Created user {user_created.username}")

        return user_created

    @api_error_handler
    def get(self, user_id: UUID) -> UserModel:
        # TODO: Implement this endpoint in the API
        response = self.http_client.get(url=f"/api/v1/users/{user_id}")
        response.raise_for_status()
        response_json = response.json()
        user = self._model_from_json(response_json=response_json)
        self.log(message=f"Got user {user.username}")
        return user

    def exist(self, user_id: UUID) -> bool:
        # TODO: Implement this endpoint in the API
        response = self.http_client.get(url=f"/api/v1/users/{user_id}")
        return response.status_code == 200

    @api_error_handler
    def delete(self, user_id: UUID) -> None:
        self.http_client.delete(url=f"/api/users/{user_id}").raise_for_status()
        self.log(message=f"Deleted user {id}")

    ####################
    # V0 API methods #
    ####################

    @api_error_handler
    def list(self) -> List[UserModel]:
        response = self.http_client.get(url="/api/users")
        response.raise_for_status()
        response_json = response.json()
        users = self._model_from_jsons(response_jsons=response_json)
        self.log(message=f"Listed {len(users)} users")
        return users

    @api_error_handler
    def list_by_workspace_id(self, workspace_id: UUID) -> List[UserModel]:
        response = self.http_client.get(url=f"/api/workspaces/{workspace_id}/users")
        response.raise_for_status()
        response_json = response.json()
        users = self._model_from_jsons(response_jsons=response_json)
        self.log(message=f"Listed {len(users)} users")
        return users

    @api_error_handler
    def get_me(self) -> UserModel:
        response = self.http_client.get("/api/me")
        response.raise_for_status()
        response_json = response.json()
        user = self._model_from_json(response_json=response_json)
        self.log(message=f"Got user {user.username}")
        return user

    @api_error_handler
    def add_to_workspace(self, workspace_id: UUID, user_id: UUID) -> "UserModel":
        response = self.http_client.post(url=f"/api/workspaces/{workspace_id}/users/{user_id}").raise_for_status()
        self.log(message=f"Added user {user_id} to workspace {workspace_id}")
        return self._model_from_json(response_json=response.json())

    @api_error_handler
    def delete_from_workspace(self, workspace_id: UUID, user_id: UUID) -> "UserModel":
        response = self.http_client.delete(url=f"/api/workspaces/{workspace_id}/users/{user_id}").raise_for_status()
        self.log(message=f"Deleted user {user_id} from workspace {workspace_id}")
        return self._model_from_json(response_json=response.json())

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json) -> UserModel:
        response_json["inserted_at"] = self._date_from_iso_format(date=response_json["inserted_at"])
        response_json["updated_at"] = self._date_from_iso_format(date=response_json["updated_at"])
        return UserModel(**response_json)

    def _model_from_jsons(self, response_jsons) -> List[UserModel]:
        return list(map(self._model_from_json, response_jsons))
