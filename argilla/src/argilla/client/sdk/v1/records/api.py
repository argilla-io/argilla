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

from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

import httpx

from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from argilla.client.sdk.v1.datasets.models import FeedbackSuggestionModel
from argilla.client.sdk.v1.records.models import FeedbackItemModel


def update_record(
    # TODO: Use the proper sdk API Model instead of the dict
    client: httpx.Client,
    id: Union[str, UUID],
    data: Dict[str, Any],
) -> Response[Union[FeedbackItemModel, ErrorMessage, HTTPValidationError]]:
    """Sends a `PATCH` request to `/api/v1/records/{id}` endpoint to partially update
    a record in Argilla.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the record to be updated in Argilla.
        data: the data to be updated in the record. It can contain `metadata` and/or
            `suggestions` fields.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is a `FeedbackItemModel`.
    """
    url = f"/api/v1/records/{id}"

    body = {}
    if "metadata" in data:
        body["metadata"] = data["metadata"]
    if "suggestions" in data:
        body["suggestions"] = data["suggestions"]
    if "vectors" in data:
        body["vectors"] = data["vectors"]

    response = client.patch(url=url, json=body)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackItemModel.parse_raw(response.content)
        return response_obj

    return handle_response_error(response)


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


def set_suggestion(
    client: httpx.Client,
    record_id: UUID,
    question_id: UUID,
    value: Any,
    type: Optional[Literal["model", "human"]] = None,
    score: Optional[float] = None,
    agent: Optional[str] = None,
) -> Response[Union[FeedbackSuggestionModel, ErrorMessage, HTTPValidationError]]:
    """Sends a PUT request to `/api/v1/records/{id}/suggestions` endpoint to add or update
    a suggestion for a question in the `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        record_id: the id of the record to add the suggestion to.
        question_id: the id of the question to add the suggestion to.
        value: the value of the suggestion.
        type: the type of the suggestion. It can be either `model` or `human`. Defaults to None.
        score: the score of the suggestion. Defaults to None.
        agent: the agent used to obtain the suggestion. Defaults to None.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a `FeedbackSuggestionModel`.
    """
    url = f"/api/v1/records/{record_id}/suggestions"

    suggestion = {
        "question_id": str(question_id),
        "value": value,
    }
    if type is not None:
        suggestion["type"] = type
    if score is not None:
        suggestion["score"] = score
    if agent is not None:
        suggestion["agent"] = agent

    response = client.put(url=url, json=suggestion)

    if response.status_code in [200, 201]:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackSuggestionModel(**response.json())
        return response_obj
    return handle_response_error(response)
