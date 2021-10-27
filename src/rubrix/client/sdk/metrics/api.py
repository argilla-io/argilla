from functools import lru_cache
from typing import Any, Dict, List, Union

import httpx

from rubrix.client import AuthenticatedClient, Response
from rubrix.client.sdk.commons.api import build_data_response, build_raw_response
from rubrix.client.sdk.commons.models import ErrorMessage, HTTPValidationError
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

    return build_data_response(response, data_type=MetricInfo)


def calculate_metric(
    client: AuthenticatedClient,
    name: str,
    task: str,
    metric: str,
    interval: float,
    size: int,
) -> Response[Union[Dict[str, Any], ErrorMessage, HTTPValidationError]]:
    url = "{}/api/datasets/{task}/{name}/metrics/{metric}:summary?interval={interval}&size={size}".format(
        client.base_url,
        name=name,
        task=task,
        metric=metric,
        interval=interval,
        size=size,
    )

    response = httpx.post(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        json={},  # TODO: parameterize !!!
    )

    return build_raw_response(response)
