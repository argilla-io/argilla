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

from typing import Union
from uuid import UUID

import httpx

from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import (
    ErrorMessage,
    HTTPValidationError,
    Response,
)
from argilla.client.sdk.v1.workspaces.models import WorkspaceModel


def get_workspace(
    client: httpx.Client,
    id: UUID,
) -> Response[Union[WorkspaceModel, ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/workspaces/{id}` endpoint to retrieve a workspace.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the workspace to be retrieved.

    Returns:
        A `Response` object with the parsed response, containing a `parsed` attribute with the
        parsed response if the request was successful, which is an instance of `WorkspaceModel`.
    """
    url = f"/api/v1/workspaces/{id}"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = WorkspaceModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)
