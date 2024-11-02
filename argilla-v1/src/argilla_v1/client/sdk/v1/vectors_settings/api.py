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

from typing import TYPE_CHECKING, Union

from argilla_v1.client.sdk.commons.errors_handler import handle_response_error
from argilla_v1.client.sdk.commons.models import Response
from argilla_v1.client.sdk.v1.vectors_settings.models import VectorSettingsModel

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla_v1.client.sdk.commons.models import ErrorMessage, HTTPValidationError


def update_vector_settings(
    client: "httpx.Client", id: Union[str, "UUID"], title: str
) -> Response[Union[VectorSettingsModel, "ErrorMessage", "HTTPValidationError"]]:
    """Sends a `PATCH` request to `/api/v1/vector_settings/{id}` endpoint to partially
    update a vector settings in Argilla.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the vector settings to be updated in Argilla.
        title: the new title of the vector settings.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is a `VectorSettingsModel`.
    """
    url = f"/api/v1/vectors-settings/{id}"

    body = {"title": title}

    response = client.patch(url=url, json=body)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = VectorSettingsModel.parse_raw(response.content)
        return response_obj

    return handle_response_error(response)


def delete_vector_settings(
    client: "httpx.Client", id: Union[str, "UUID"]
) -> Response[Union[VectorSettingsModel, "ErrorMessage", "HTTPValidationError"]]:
    """Sends a `DELETE` request to `/api/v1/vector_settings/{id}` endpoint to delete
    a vector settings in Argilla.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the vector settings to be deleted in Argilla.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is a `VectorSettingsModel`.
    """
    url = f"/api/v1/vectors-settings/{id}"

    response = client.delete(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = VectorSettingsModel.parse_raw(response.content)
        return response_obj

    return handle_response_error(response)
