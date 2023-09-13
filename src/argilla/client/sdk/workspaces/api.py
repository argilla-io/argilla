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

from typing import List, Union
from uuid import UUID

import httpx

from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from argilla.client.sdk.users.models import UserModel
from argilla.client.sdk.workspaces.models import WorkspaceModel


def list_workspaces(client: httpx.Client) -> Response[Union[List[WorkspaceModel], ErrorMessage, HTTPValidationError]]:
    """Sends a request to `GET /api/workspaces` to list all the workspaces in the account.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.

    Returns:
        A Response object with the parsed response, containing a `parsed` attribute with the
        parsed response if the request was successful, which is a list of `WorkspaceModel` objects.
    """
    url = "/api/workspaces"

    response = client.get(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = [WorkspaceModel(**workspace) for workspace in response.json()]
        return response_obj
    return handle_response_error(response)


def create_workspace(
    client: httpx.Client, name: str
) -> Response[Union[WorkspaceModel, ErrorMessage, HTTPValidationError]]:
    """Sends a request to `POST /api/workspaces` to create a new workspace.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        name: the name of the workspace to be created.

    Returns:
        A Response object with the parsed response, containing a `parsed` attribute with the
        parsed response if the request was successful, which is a `WorkspaceModel` object.
    """
    url = "/api/workspaces"

    response = client.post(url=url, json={"name": name})

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = WorkspaceModel(**response.json())
        return response_obj
    return handle_response_error(response)


def list_workspace_users(
    client: httpx.Client, id: UUID
) -> Response[Union[List[UserModel], ErrorMessage, HTTPValidationError]]:
    """Sends a request to `GET /api/workspaces/{id}/users` to list all the users in the workspace.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the workspace to list the users from.

    Returns:
        A Response object with the parsed response, containing a `parsed` attribute with the
        parsed response if the request was successful, which is a list of `UserModel` objects.
    """
    url = f"/api/workspaces/{id}/users"

    response = client.get(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = [UserModel(**user) for user in response.json()]
        return response_obj
    return handle_response_error(response)


def create_workspace_user(
    client: httpx.Client, id: UUID, user_id: UUID
) -> Response[Union[UserModel, ErrorMessage, HTTPValidationError]]:
    """Sends a request to `POST /api/workspaces/{id}/users/{user_id}` to add a new user to the workspace.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the workspace to create the user in.
        user_id: the id of the user to be added to the workspace.

    Returns:
        A Response object with the parsed response, containing a `parsed` attribute with the
        parsed response if the request was successful, which is a `UserModel` object.
    """
    url = f"/api/workspaces/{id}/users/{user_id}"

    response = client.post(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = UserModel(**response.json())
        return response_obj
    return handle_response_error(response)


def delete_workspace_user(
    client: httpx.Client, id: UUID, user_id: UUID
) -> Response[Union[UserModel, ErrorMessage, HTTPValidationError]]:
    """Sends a request to `DELETE /api/workspaces/{id}/users/{user_id}` to remove a user from the workspace.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the workspace to remove the user from.
        user_id: the id of the user to be removed from the workspace.

    Returns:
        A Response object with the parsed response, containing a `parsed` attribute with the
        parsed response if the request was successful, which is a `UserModel` object.
    """
    url = f"/api/workspaces/{id}/users/{user_id}"

    response = client.delete(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = UserModel(**response.json())
        return response_obj
    return handle_response_error(response)
