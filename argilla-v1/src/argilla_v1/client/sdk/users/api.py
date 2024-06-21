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

from typing import List, Optional, Union
from uuid import UUID

import httpx

from argilla_v1.client.sdk.client import AuthenticatedClient
from argilla_v1.client.sdk.commons.errors_handler import handle_response_error
from argilla_v1.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from argilla_v1.client.sdk.users.models import UserCreateModel, UserModel, UserRole


# TODO(alvarobartt,frascuchon): use ONLY `httpx.Client` instead of `AuthenticatedClient` and
# fix mock in `tests/conftest.py` to use `httpx.Client` instead of `AuthenticatedClient`
def whoami(client: AuthenticatedClient) -> UserModel:
    """Sends a GET request to `/api/me` endpoint to get the current user information.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.

    Returns:
        A `UserModel` instance with the current user information.
    """
    url = "/api/me"

    response = client.get(url)
    return UserModel(**response)


# TODO(frascuchon): rename this to `whoami` and deprecate the current `whoami` function
# in favor of this one, as this is just a patch.
def whoami_httpx(client: httpx.Client) -> Response[Union[UserModel, ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/me` endpoint to get the current user information.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is an instance of `UserModel`.
    """
    url = "/api/me"

    response = client.get(url)

    if response.status_code == 200:
        parsed_response = UserModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def list_users(client: httpx.Client) -> Response[Union[List[UserModel], ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/users` endpoint to get the list of users.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is a list of `UserModel` instances.
    """
    url = "/api/users"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = [UserModel(**user) for user in response.json()]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def create_user(
    client: httpx.Client,
    first_name: str,
    username: str,
    password: str,
    last_name: Optional[str] = None,
    role: UserRole = UserRole.annotator,
    workspaces: Optional[List[str]] = None,
) -> Response[Union[UserModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/users` endpoint to create a new user.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        first_name: the first name of the user. Must be a string of at least 1 character.
        last_name: the last name of the user. Is optional and defaults to `None`, but if provided
            must be a string of at least 1 character.
        username: the username of the user. Must be a string matching the following regex:
            ^(?!-|_)[a-z0-9-_]+$.
        role: the role of the user. Available roles are: `admin`, and `annotator`.
        password: the password of the user. Must be a string between 8 and 100 characters.
        workspaces: a list of workspace names to which the user will be linked to.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is an instance of `UserModel`.
    """
    url = "/api/users"

    user = UserCreateModel(
        first_name=first_name,
        last_name=last_name,
        username=username,
        role=role,
        password=password,
        workspaces=workspaces,
    )

    response = client.post(
        url=url,
        json=user.dict(exclude_none=True),
    )

    if response.status_code == 200:
        parsed_response = UserModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def delete_user(client: httpx.Client, user_id: UUID) -> Response[Union[UserModel, ErrorMessage, HTTPValidationError]]:
    """Sends a DELETE request to `/api/users/{user_id}` endpoint to delete a user.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        user_id: the id of the user to be deleted.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is an instance of `UserModel`.
    """
    url = f"/api/users/{user_id}"

    response = client.delete(url=url)

    if response.status_code == 200:
        parsed_response = UserModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)
