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

from typing import List, Union

import httpx

from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import (
    ErrorMessage,
    HTTPValidationError,
    Response,
)
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
        parsed_response = [WorkspaceModel(**workspace) for workspace in response.json()]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)
