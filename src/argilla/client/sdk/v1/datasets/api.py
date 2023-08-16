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

import warnings
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

import httpx

from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from argilla.client.sdk.v1.datasets.models import (
    FeedbackDatasetModel,
    FeedbackFieldModel,
    FeedbackMetricsModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
    FeedbackSuggestionModel,
)


def create_dataset(
    client: httpx.Client, name: str, workspace_id: UUID, guidelines: Optional[str] = None
) -> Response[Union[FeedbackDatasetModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets` endpoint to create a new `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        name: the name of the dataset to be created.
        workspace_id: the id of the workspace where the dataset will be created.
        guidelines: the guidelines of the dataset to be created. Defaults to `None`.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is an instance of `FeedbackDatasetModel`.
    """
    url = "/api/v1/datasets"

    body = {"name": name, "workspace_id": str(workspace_id)}
    if guidelines is not None:
        body.update({"guidelines": guidelines})

    response = client.post(url=url, json=body)

    if response.status_code == 201:
        parsed_response = FeedbackDatasetModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def get_dataset(
    client: httpx.Client, id: UUID
) -> Response[Union[FeedbackDatasetModel, ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}` endpoint to retrieve a `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to be retrieved.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is an instance of `FeedbackDatasetModel`.
    """
    url = f"/api/v1/datasets/{id}"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = FeedbackDatasetModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def delete_dataset(client: httpx.Client, id: UUID) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    """Sends a DELETE request to `/api/v1/datasets/{id}` endpoint to delete a `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to be deleted.

    Returns:
        A `Response` object with the response itself, and/or the error codes if applicable.
    """
    url = f"/api/v1/datasets/{id}"

    response = client.delete(url=url)

    if response.status_code == 200:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
        )
    return handle_response_error(response)


def publish_dataset(
    client: httpx.Client, id: UUID
) -> Response[Union[FeedbackDatasetModel, ErrorMessage, HTTPValidationError]]:
    """Sends a PUT request to `/api/v1/datasets/{id}/publish` endpoint to publish a `FeedbackDataset`.
    Publishing in Argilla means setting the status of the dataset from `draft` to `ready`, so that
    it can be used to add records to it.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to be published.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is an instance of `FeedbackDatasetModel`.
    """
    url = f"/api/v1/datasets/{id}/publish"

    response = client.put(url=url)

    if response.status_code == 200:
        parsed_response = FeedbackDatasetModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def list_datasets(
    client: httpx.Client,
) -> Response[Union[List[FeedbackDatasetModel], ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets` endpoint to retrieve a list of `FeedbackTask` datasets.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a list of `FeedbackDatasetModel`.
    """
    url = "/api/v1/me/datasets"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = [FeedbackDatasetModel(**dataset) for dataset in response.json()["items"]]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def get_records(
    client: httpx.Client, id: UUID, offset: int = 0, limit: int = 50
) -> Response[Union[FeedbackRecordsModel, ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}/records` endpoint to retrieve a list of `FeedbackTask` records.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to retrieve the records from.
        offset: the offset to be used in the pagination. Defaults to 0.
        limit: the limit to be used in the pagination. Defaults to 50.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is an instance of `FeedbackRecordsModel`.
    """
    url = f"/api/v1/datasets/{id}/records"

    params = {"include": ["responses", "suggestions"], "offset": offset, "limit": limit}

    response = client.get(url=url, params=params)

    if response.status_code == 200:
        parsed_response = FeedbackRecordsModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def add_records(
    client: httpx.Client, id: UUID, records: List[Dict[str, Any]]
) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets/{id}/records` endpoint to add a list of `FeedbackTask` records.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to add the records to.
        records: the list of records to be added to the dataset.

    Returns:
        A `Response` object with the response itself, and/or the error codes if applicable.
    """
    url = f"/api/v1/datasets/{id}/records"

    active_user_id = None

    for record in records:
        cleaned_responses = []
        response_without_user_id = False
        for response in record.get("responses", []):
            if response.get("user_id") is None:
                if response_without_user_id:
                    warnings.warn(
                        f"Multiple responses without `user_id` found in record {record}, so just the first one will be"
                        " used while the rest will be ignored."
                    )
                    continue
                else:
                    if active_user_id is None:
                        active_user_id = client.get("api/me").json()["id"]
                    response["user_id"] = active_user_id
                response_without_user_id = True
            if isinstance(response.get("user_id"), UUID):
                response["user_id"] = str(response.get("user_id"))
            cleaned_responses.append(response)
        record["responses"] = cleaned_responses

        for suggestion in record.get("suggestions", []):
            if isinstance(suggestion.get("question_id"), UUID):
                suggestion["question_id"] = str(suggestion.get("question_id"))

    response = client.post(url=url, json={"items": records})

    if response.status_code == 204:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
        )
    return handle_response_error(response)


def get_fields(
    client: httpx.Client, id: UUID
) -> Response[Union[List[FeedbackFieldModel], ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}/fields` endpoint to retrieve a list of `FeedbackTask` fields.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to retrieve the fields from.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a list of `FeedbackFieldModel`.
    """
    url = f"/api/v1/datasets/{id}/fields"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = [FeedbackFieldModel(**item) for item in response.json()["items"]]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def add_field(
    client: httpx.Client, id: UUID, field: Dict[str, Any]
) -> Response[Union[FeedbackFieldModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets/{id}/fields` endpoint to add a `FeedbackTask` field.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to add the field to.
        field: the field to be added to the dataset.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is an instance of `FeedbackFieldModel`.
    """
    url = f"/api/v1/datasets/{id}/fields"

    response = client.post(url=url, json=field)

    if response.status_code == 201:
        parsed_response = FeedbackFieldModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def get_questions(
    client: httpx.Client, id: UUID
) -> Response[Union[List[FeedbackQuestionModel], ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}/questions` endpoint to retrieve a
    list of `FeedbackTask` questions.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to retrieve the questions from.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a list of `FeedbackQuestionModel`.
    """
    url = f"/api/v1/datasets/{id}/questions"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = [FeedbackQuestionModel(**item) for item in response.json()["items"]]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def add_question(
    client: httpx.Client, id: UUID, question: Dict[str, Any]
) -> Response[Union[FeedbackQuestionModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets/{id}/questions` endpoint to add a
    question to the `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a `FeedbackQuestionModel`.
    """
    url = f"/api/v1/datasets/{id}/questions"

    response = client.post(url=url, json=question)

    if response.status_code == 201:
        parsed_response = FeedbackQuestionModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
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
        parsed_response = FeedbackSuggestionModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def get_metrics(
    client: httpx.Client,
    id: UUID,
) -> Response[Union[FeedbackMetricsModel, ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}/metrics` endpoint to retrieve the metrics
    of a `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to retrieve the metrics from.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a `FeedbackMetricsModel`.
    """
    url = f"/api/v1/me/datasets/{id}/metrics"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = FeedbackMetricsModel(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)
