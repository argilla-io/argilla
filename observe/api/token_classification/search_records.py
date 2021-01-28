from typing import Any, Dict, List, Optional, Union, cast

import httpx
from attr import asdict

from ...client import AuthenticatedClient, Client
from ...types import Response

from ...models.body_search_records_token_classification_datasets_dataset_id__search_post import (
    BodySearchRecordsTokenClassificationDatasets_DatasetId__SearchPost,
)
from ...models.token_classification_results import TokenClassificationResults
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import Dict
from typing import Union


def _get_kwargs(
    *,
    client: Client,
    dataset_id: str,
    json_body: BodySearchRecordsTokenClassificationDatasets_DatasetId__SearchPost,
    limit: Union[Unset, int] = 500,
    from_: Union[Unset, int] = 0,
) -> Dict[str, Any]:
    url = "{}/token-classification/datasets/{dataset_id}/:search".format(client.base_url, dataset_id=dataset_id)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if limit is not UNSET:
        params["limit"] = limit
    if from_ is not UNSET:
        params["from"] = from_

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[TokenClassificationResults, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = TokenClassificationResults.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[TokenClassificationResults, HTTPValidationError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    dataset_id: str,
    json_body: BodySearchRecordsTokenClassificationDatasets_DatasetId__SearchPost,
    limit: Union[Unset, int] = 500,
    from_: Union[Unset, int] = 0,
) -> Response[Union[TokenClassificationResults, HTTPValidationError]]:
    kwargs = _get_kwargs(client=client, dataset_id=dataset_id, json_body=json_body, limit=limit, from_=from_,)

    response = httpx.post(**kwargs,)

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    dataset_id: str,
    json_body: BodySearchRecordsTokenClassificationDatasets_DatasetId__SearchPost,
    limit: Union[Unset, int] = 500,
    from_: Union[Unset, int] = 0,
) -> Optional[Union[TokenClassificationResults, HTTPValidationError]]:
    """  """

    return sync_detailed(client=client, dataset_id=dataset_id, json_body=json_body, limit=limit, from_=from_,).parsed


async def asyncio_detailed(
    *,
    client: Client,
    dataset_id: str,
    json_body: BodySearchRecordsTokenClassificationDatasets_DatasetId__SearchPost,
    limit: Union[Unset, int] = 500,
    from_: Union[Unset, int] = 0,
) -> Response[Union[TokenClassificationResults, HTTPValidationError]]:
    kwargs = _get_kwargs(client=client, dataset_id=dataset_id, json_body=json_body, limit=limit, from_=from_,)

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    dataset_id: str,
    json_body: BodySearchRecordsTokenClassificationDatasets_DatasetId__SearchPost,
    limit: Union[Unset, int] = 500,
    from_: Union[Unset, int] = 0,
) -> Optional[Union[TokenClassificationResults, HTTPValidationError]]:
    """  """

    return (
        await asyncio_detailed(client=client, dataset_id=dataset_id, json_body=json_body, limit=limit, from_=from_,)
    ).parsed
