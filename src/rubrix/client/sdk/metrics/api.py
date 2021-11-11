from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.api import build_list_response, build_raw_response
from rubrix.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from rubrix.client.sdk.metrics.models import MetricInfo


@lru_cache()
def get_dataset_metrics(
    client: AuthenticatedClient, name: str, task: str
) -> Response[Union[List[MetricInfo], ErrorMessage, HTTPValidationError]]:
    url = "{}/api/datasets/{task}/{name}/metrics".format(
        client.base_url, name=name, task=task
    )

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

    response = httpx.post(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        json={"query_text": query},
    )

    return build_raw_response(response)
