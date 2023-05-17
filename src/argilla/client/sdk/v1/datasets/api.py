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

from typing import Any, Dict, List, Optional, Union

import httpx

from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import (
    ErrorMessage,
    HTTPValidationError,
    Response,
)
from argilla.client.sdk.v1.datasets.models import (
    FeedbackDatasetModel,
    FeedbackFieldModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
)


def create_dataset(
    client: httpx.Client,
    name: str,
    workspace_id: str,
    guidelines: Optional[str] = None,
) -> Response[Union[FeedbackDatasetModel, ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets"

    body = {"name": name, "workspace_id": workspace_id}
    if guidelines is not None:
        body.update({"guidelines": guidelines})

    response = client.post(url=url, json=body)

    if response.status_code == 201:
        parsed_response = FeedbackDatasetModel.construct(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def get_dataset(
    client: httpx.Client,
    id: str,
) -> Response[Union[FeedbackDatasetModel, ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets/{id}".format(id=id)

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = FeedbackDatasetModel.construct(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def delete_dataset(
    client: httpx.Client,
    id: str,
) -> Response:
    url = "/api/v1/datasets/{id}".format(id=id)

    response = client.delete(url=url)

    if response.status_code == 200:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
        )
    return handle_response_error(response)


def publish_dataset(
    client: httpx.Client,
    id: str,
) -> Response[Union[FeedbackDatasetModel, ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets/{id}/publish".format(id=id)

    response = client.put(url=url)

    if response.status_code == 200:
        parsed_response = FeedbackDatasetModel.construct(**response.json())
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
    url = "/api/v1/me/datasets"

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = [FeedbackDatasetModel.construct(**dataset) for dataset in response.json()["items"]]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def get_records(
    client: httpx.Client,
    id: str,
    offset: int = 0,
    limit: int = 50,
) -> Response[Union[FeedbackRecordsModel, ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/me/datasets/{id}/records".format(id=id)

    response = client.get(
        url=url,
        params={"include": "responses", "offset": offset, "limit": limit},
    )

    if response.status_code == 200:
        parsed_response = FeedbackRecordsModel.construct(**response.json())
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def add_records(
    client: httpx.Client,
    id: str,
    records: List[Dict[str, Any]],
) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets/{id}/records".format(id=id)

    response = client.post(url=url, json={"items": records})

    if response.status_code == 204:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
        )
    return handle_response_error(response)


def get_fields(
    client: httpx.Client,
    id: str,
) -> Response[Union[List[FeedbackFieldModel], ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets/{id}/fields".format(id=id)

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = [FeedbackFieldModel.construct(**item) for item in response.json()["items"]]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def add_field(
    client: httpx.Client,
    id: str,
    field: Dict[str, Any],
) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets/{id}/fields".format(id=id)

    response = client.post(url=url, json=field)

    if response.status_code == 201:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
        )
    return handle_response_error(response)


def get_questions(
    client: httpx.Client,
    id: str,
) -> Response[Union[List[FeedbackQuestionModel], ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets/{id}/questions".format(id=id)

    response = client.get(url=url)

    if response.status_code == 200:
        parsed_response = [FeedbackQuestionModel.construct(**item) for item in response.json()["items"]]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )
    return handle_response_error(response)


def add_question(
    client: httpx.Client,
    id: str,
    question: Dict[str, Any],
) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    url = "/api/v1/datasets/{id}/questions".format(id=id)

    response = client.post(url=url, json=question)

    if response.status_code == 201:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
        )
    return handle_response_error(response)
