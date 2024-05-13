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

from functools import lru_cache
from typing import List, Optional, Union

import httpx

from argilla._constants import WORKSPACE_HEADER_NAME
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import Response
from argilla.client.sdk.datasets.models import CopyDatasetRequest, Dataset


@lru_cache(maxsize=None)
def get_dataset(client: AuthenticatedClient, name: str, workspace: Optional[str] = None) -> Response[Dataset]:
    url = f"{client.base_url}/api/datasets/{name}"

    params = {"workspace": workspace} if workspace else None

    response = httpx.get(
        url=url,
        params=params,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = Dataset(**response.json())
        return response_obj

    handle_response_error(response)


def list_datasets(client: AuthenticatedClient, workspace: Optional[str] = None) -> Response[List[Dataset]]:
    url = f"{client.base_url}/api/datasets"

    headers = client.get_headers().copy()
    headers.pop(WORKSPACE_HEADER_NAME, None)

    response = httpx.get(
        url=url,
        params={"workspace": workspace} if workspace else None,
        headers=headers,
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = [Dataset(**dataset) for dataset in response.json()]
        return response_obj
    handle_response_error(response)


def copy_dataset(client: AuthenticatedClient, name: str, json_body: CopyDatasetRequest) -> Response[Dataset]:
    url = f"{client.base_url}/api/datasets/{name}:copy"

    response = httpx.put(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        json=json_body.dict(by_alias=True),
    )

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = Dataset(**response.json())
        return response_obj
    handle_response_error(response)


def delete_dataset(client: AuthenticatedClient, name: str) -> Response:
    url = f"{client.base_url}/api/datasets/{name}"

    response = httpx.delete(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )
    # If everything was ok, we must clear local cache data
    if 200 <= response.status_code < 400:
        get_dataset.cache_clear()
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=response.json(),
        )
    handle_response_error(response, dataset=name)
