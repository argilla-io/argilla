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
from typing import Union

import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from rubrix.client.sdk.datasets.models import CopyDatasetRequest, Dataset


@lru_cache(maxsize=None)
def get_dataset(
    client: AuthenticatedClient,
    name: str,
) -> Response[Union[Dataset, ErrorMessage, HTTPValidationError]]:
    url = "{}/api/datasets/{name}".format(client.base_url, name=name)

    response = httpx.get(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    return _build_response(response=response)


def copy_dataset(
    client: AuthenticatedClient,
    name: str,
    json_body: CopyDatasetRequest,
) -> Response[Union[Dataset, ErrorMessage, HTTPValidationError]]:
    url = "{}/api/datasets/{name}:copy".format(client.base_url, name=name)

    response = httpx.put(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        json=json_body.dict(by_alias=True),
    )

    return _build_response(response=response)


def delete_dataset(
    client: AuthenticatedClient,
    name: str,
) -> httpx.Response:
    url = "{}/api/datasets/{name}".format(client.base_url, name=name)

    response = httpx.delete(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )
    # If everything was ok, we must clear local cache data
    if response.status_code == 200:
        get_dataset.cache_clear()

    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=response.json(),
    )


def _build_response(
    response: httpx.Response,
) -> Response[Union[Dataset, ErrorMessage, HTTPValidationError]]:

    parsed_response = None
    if response.status_code == 200:
        parsed_response = Dataset(**response.json())
    elif response.status_code == 404:
        parsed_response = ErrorMessage(**response.json())
    elif response.status_code == 500:
        parsed_response = ErrorMessage(**response.json())
    elif response.status_code == 422:
        parsed_response = HTTPValidationError(**response.json())

    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=parsed_response,
    )
