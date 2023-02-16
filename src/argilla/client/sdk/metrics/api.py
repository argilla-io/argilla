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
from typing import Any, Dict, List, Optional, Union

import httpx

from argilla.client.sdk._helpers import build_raw_response
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.api import build_list_response
from argilla.client.sdk.commons.models import (
    ErrorMessage,
    HTTPValidationError,
    Response,
)
from argilla.client.sdk.metrics.models import MetricInfo


@lru_cache()
def get_dataset_metrics(
    client: AuthenticatedClient, name: str, task: str
) -> Response[Union[List[MetricInfo], ErrorMessage, HTTPValidationError]]:
    url = "{}/api/datasets/{task}/{name}/metrics".format(client.base_url, name=name, task=task)

    response = httpx.get(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    return build_list_response(response, item_class=MetricInfo)


def compute_metric(
    client: AuthenticatedClient,
    name: str,
    task: str,
    metric: str,
    query: Optional[str] = None,
    **query_params,
) -> Response[Union[Dict[str, Any], ErrorMessage, HTTPValidationError]]:
    url = "{}/api/datasets/{task}/{name}/metrics/{metric}:summary".format(
        client.base_url, task=task, name=name, metric=metric
    )

    query_params = {k: v for k, v in query_params.items() if v is not None}
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])

    if query == "":
        query = None

    response = httpx.post(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        json={"query_text": query},
    )

    return build_raw_response(response)
