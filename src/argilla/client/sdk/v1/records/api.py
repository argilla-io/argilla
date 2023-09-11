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
from argilla.client.sdk.v1.records.models import FeedbackItemModel


def delete_record(
    client: httpx.Client, id: UUID
) -> Response[Union[FeedbackItemModel, ErrorMessage, HTTPValidationError]]:
    """Sends a DELETE request to `/api/v1/records/{id}` endpoint to delete a
    record from Argilla.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the record to be deleted in Argilla.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is a `FeedbackItemModel`.
    """
    url = f"/api/v1/records/{id}"

    response = client.delete(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackItemModel.parse_raw(response.content)
        return response_obj
    return handle_response_error(response)


def delete_suggestions(
    client: httpx.Client, id: UUID, suggestion_ids: List[UUID]
) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    """Sends a DELETE request to `/api/v1/records/{id}/suggestions` endpoint to delete
    suggestions from a record in Argilla.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the record in Argilla.
        suggestion_ids: the ids of the suggestions to be deleted from the record.

    Returns:
        A `Response` object with the response itself, and/or the error codes if applicable.
    """
    url = f"/api/v1/records/{id}/suggestions"
    params = {"ids": ",".join([str(suggestion_id) for suggestion_id in suggestion_ids])}

    response = client.delete(url=url, params=params)

    if response.status_code == 204:
        return Response.from_httpx_response(response)
    return handle_response_error(response)
