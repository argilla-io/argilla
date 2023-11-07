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
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import httpx

from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from argilla.client.sdk.v1.datasets.models import (
    FeedbackDatasetModel,
    FeedbackFieldModel,
    FeedbackListVectorSettingsModel,
    FeedbackMetadataPropertyModel,
    FeedbackMetricsModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
    FeedbackRecordsSearchModel,
    FeedbackRecordsSearchVectorQuery,
    FeedbackResponseStatusFilter,
    FeedbackVectorSettingsModel,
)


def create_dataset(
    client: httpx.Client,
    name: str,
    workspace_id: Union[str, UUID],
    guidelines: Optional[str] = None,
    allow_extra_metadata: bool = True,
) -> Response[Union[FeedbackDatasetModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets` endpoint to create a new `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        name: the name of the dataset to be created.
        workspace_id: the id of the workspace where the dataset will be created.
        guidelines: the guidelines of the dataset to be created. Defaults to `None`.
        allow_extra_metadata: whether to allow extra metadata not defined as a metadata property. Defaults to `True`.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is an instance of `FeedbackDatasetModel`.
    """
    url = "/api/v1/datasets"

    body = {"name": name, "workspace_id": str(workspace_id), "allow_extra_metadata": allow_extra_metadata}
    if guidelines is not None:
        body.update({"guidelines": guidelines})

    response = client.post(url=url, json=body)

    if response.status_code == 201:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackDatasetModel(**response.json())
        return response_obj
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
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackDatasetModel(**response.json())
        return response_obj
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
        return Response.from_httpx_response(response)
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
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackDatasetModel(**response.json())
        return response_obj
    return handle_response_error(response)


def list_datasets(
    client: httpx.Client,
    workspace_id: Optional[UUID] = None,
) -> Response[Union[list, List[FeedbackDatasetModel], ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/me/datasets` endpoint to retrieve a list of
    `FeedbackTask` datasets filtered by `workspace_id` if applicable.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        workspace_id: the id of the workspace to filter the datasets by. Note that the user
            should either be owner or have access to the workspace. Defaults to None.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a list of `FeedbackDatasetModel` if any, otherwise
        it will contain an empty list.
    """
    url = "/api/v1/me/datasets"

    params = {}
    if workspace_id is not None:
        params["workspace_id"] = str(workspace_id)

    response = client.get(url=url, params=params)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = [FeedbackDatasetModel(**dataset) for dataset in response.json()["items"]]
        return response_obj
    return handle_response_error(response)


def get_records(
    client: httpx.Client,
    id: UUID,
    include: Union[None, List[str]] = None,
    offset: int = 0,
    limit: int = 50,
    response_status: Optional[List[FeedbackResponseStatusFilter]] = None,
    metadata_filters: Optional[List[str]] = None,
    sort_by: Optional[List[str]] = None,
) -> Response[Union[FeedbackRecordsModel, ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}/records` endpoint to retrieve a
    list of `FeedbackTask` records.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to retrieve the records from.
        include: the fields to be included in the response.
             Can either be `responses`, `suggestions`, `vectors:all` or `vectors:vector_name_1,vector_name_2,...`
        offset: the offset to be used in the pagination. Defaults to 0.
        limit: the limit to be used in the pagination. Defaults to 50.
        response_status: the status of the responses to be retrieved. Can either be
            `draft`, `missing`, `discarded`, or `submitted`. Defaults to None.
        metadata_filters: the metadata filters to be applied to the records. Defaults to None.
        sort_by: the fields to be used to sort the records. Defaults to None.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is an instance of `FeedbackRecordsModel`.
    """
    url = f"/api/v1/datasets/{id}/records"
    params = {"offset": offset, "limit": limit}

    if include:
        params["include"] = include

    if response_status:
        params["response_status"] = response_status

    if metadata_filters:
        params["metadata"] = metadata_filters

    if sort_by:
        params["sort_by"] = sort_by

    response = client.get(url=url, params=params)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackRecordsModel(**response.json())
        return response_obj
    return handle_response_error(response)


def search_records(
    client: httpx.Client,
    id: UUID,
    vector_query: FeedbackRecordsSearchVectorQuery,
    include: Union[None, List[str]] = None,
    response_status: Optional[List[FeedbackResponseStatusFilter]] = None,
    metadata_filters: Optional[List[str]] = None,
    limit: int = 50,
) -> Response[Union[FeedbackRecordsSearchModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets/{id}/records/search` endpoint to search for records inside an specific dataset.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to add the records to.
        include: the fields to be included in the response.
        vector_query: the vector query to be used to search for records.
        response_status: the status of the responses to be retrieved.
            Can either be `draft`, `missing`, `discarded`, or `submitted`. Defaults to None.
        metadata_filters: the metadata filters to be applied to the records. Defaults to None.
        limit: an optional value to limit the number of returned records by the search.

    Returns:
        A `Response` object with the response itself, and/or the error codes if applicable.
    """
    url = f"/api/v1/datasets/{id}/records/search"

    params = {"limit": limit}
    if include:
        params["include"] = include
    if response_status:
        params["response_status"] = response_status
    if metadata_filters:
        params["metadata"] = metadata_filters

    vector_json = {"name": vector_query.name}
    if vector_query.value:
        vector_json["value"] = vector_query.value
    if vector_query.record_id:
        vector_json["record_id"] = str(vector_query.record_id)

    json = {"query": {"vector": vector_json}}

    response = client.post(url=url, params=params, json=json)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackRecordsSearchModel(**response.json())

        return response_obj

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
        if len(cleaned_responses) > 0:
            record["responses"] = cleaned_responses

        for suggestion in record.get("suggestions", []):
            if isinstance(suggestion.get("question_id"), UUID):
                suggestion["question_id"] = str(suggestion.get("question_id"))

    response = client.post(url=url, json={"items": records})

    if response.status_code == 204:
        return Response.from_httpx_response(response)
    return handle_response_error(response)


def update_records(
    client: httpx.Client, id: UUID, records: List[Dict[str, Any]]
) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    """Sends a PATCH requests to `/api/v1/datasets/{id}/records` endpoint to update a
    a list of `FeedbackTask` records from a `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to update the records from.
        records: the list of records to be updated.

    Returns:
        A `Response` object with the response itself, and/or the error codes if applicable.
    """
    url = f"/api/v1/datasets/{id}/records"

    items = []
    for record in records:
        item = {"id": record["id"]}
        if "metadata" in record:
            item["metadata"] = record["metadata"]
        if "suggestions" in record:
            item["suggestions"] = record["suggestions"]
        if "vectors" in record:
            item["vectors"] = record["vectors"]

        items.append(item)

    response = client.patch(url=url, json={"items": items})

    if response.status_code == 204:
        return Response.from_httpx_response(response)

    return handle_response_error(response)


def delete_records(
    client: httpx.Client, id: UUID, record_ids: List[UUID]
) -> Response[Union[ErrorMessage, HTTPValidationError]]:
    """Sends a DELETE request to `/api/v1/{id}/records` endpoint to remove a list of `FeedbackDataset` records.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to remove the records from.
        record_ids: the IDs of the records to be removed from the dataset.

    Returns:
        A `Response` object with the response itself, and/or the errors codes if applicable.
    """
    url = f"/api/v1/datasets/{id}/records"

    uuids_str = ",".join([str(record_id) for record_id in record_ids])
    response = client.delete(url=url, params={"ids": uuids_str})

    if response.status_code == 204:
        return Response.from_httpx_response(response)
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
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = [FeedbackFieldModel(**item) for item in response.json()["items"]]
        return response_obj
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
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackFieldModel(**response.json())
        return response_obj
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
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = [FeedbackQuestionModel(**item) for item in response.json()["items"]]
        return response_obj
    return handle_response_error(response)


def add_question(
    client: httpx.Client, id: UUID, question: Dict[str, Any]
) -> Response[Union[FeedbackQuestionModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets/{id}/questions` endpoint to add a
    question to the `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to add the question to.
        question: the question to be added to the dataset.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a `FeedbackQuestionModel`.
    """
    url = f"/api/v1/datasets/{id}/questions"

    response = client.post(url=url, json=question)

    if response.status_code == 201:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackQuestionModel(**response.json())
        return response_obj
    return handle_response_error(response)


def get_metadata_properties(
    client: httpx.Client, id: UUID
) -> Response[Union[List[FeedbackMetadataPropertyModel], ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}/metadata-properties` endpoint to
    retrieve a list of `FeedbackDataset` metadata properties.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to retrieve the metadata properties from.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a list of `FeedbackMetadataPropertyModel`.
    """
    url = f"/api/v1/me/datasets/{id}/metadata-properties"

    response = client.get(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = [FeedbackMetadataPropertyModel(**item) for item in response.json()["items"]]
        return response_obj
    return handle_response_error(response)


def add_metadata_property(
    client: httpx.Client, id: UUID, metadata_property: Dict[str, Any]
) -> Response[Union[FeedbackMetadataPropertyModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets/{id}/metadata-properties` endpoint to
    add a metadata property to the `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to add the metadata property to.
        metadata_property: the metadata property to be added to the dataset.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a `FeedbackMetadataPropertyModel`.
    """
    url = f"/api/v1/datasets/{id}/metadata-properties"

    response = client.post(url=url, json=metadata_property)

    if response.status_code == 201:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackMetadataPropertyModel(**response.json())
        return response_obj
    return handle_response_error(response)


def list_vectors_settings(
    client: httpx.Client,
    id: UUID,
) -> Response[Union[FeedbackListVectorSettingsModel, ErrorMessage, HTTPValidationError]]:
    """Sends a GET request to `/api/v1/datasets/{id}/vectors-settings` endpoint to
    retrieve the vectors settings of a `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to retrieve the vector settings from.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if the
        request was successful, which is a `FeedbackListVectorSettingsModel`.
    """
    url = f"/api/v1/datasets/{id}/vectors-settings"

    response = client.get(url=url)
    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackListVectorSettingsModel(**response.json())
        return response_obj

    return handle_response_error(response)


def add_vector_settings(
    client: httpx.Client,
    id: UUID,
    name: str,
    title: str,
    dimensions: int,
) -> Response[Union[FeedbackVectorSettingsModel, ErrorMessage, HTTPValidationError]]:
    """Sends a POST request to `/api/v1/datasets/{id}/vectors-settings` endpoint to
    add a vector settings to the `FeedbackDataset`.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the dataset to add the vector settings to.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is a `FeedbackVectorSettingsModel`.
    """
    url = f"/api/v1/datasets/{id}/vectors-settings"

    body = {
        "name": name,
        "title": title,
        "dimensions": dimensions,
    }

    response = client.post(url=url, json=body)
    if response.status_code == 201:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackVectorSettingsModel(**response.json())
        return response_obj

    # TODO: better handle error for v1 API endpoints
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
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackMetricsModel(**response.json())
        return response_obj
    return handle_response_error(response)
