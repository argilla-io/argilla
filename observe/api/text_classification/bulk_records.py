from typing import Any, Dict, List, Optional, Union, cast

import httpx
from attr import asdict

from ...client import AuthenticatedClient, Client
from ...types import Response

from typing import cast
from ...models.http_validation_error import HTTPValidationError
from ...models.text_classification_records_bulk import TextClassificationRecordsBulk
from typing import Dict
from ...models.bulk_response import BulkResponse


def _get_kwargs(*, client: Client, json_body: TextClassificationRecordsBulk,) -> Dict[str, Any]:
    url = "{}/classification/datasets/:bulk-records".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[BulkResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BulkResponse.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[BulkResponse, HTTPValidationError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *, client: Client, json_body: TextClassificationRecordsBulk,
) -> Response[Union[BulkResponse, HTTPValidationError]]:
    kwargs = _get_kwargs(client=client, json_body=json_body,)

    response = httpx.post(**kwargs,)

    return _build_response(response=response)


def sync(
    *, client: Client, json_body: TextClassificationRecordsBulk,
) -> Optional[Union[BulkResponse, HTTPValidationError]]:
    """  """

    return sync_detailed(client=client, json_body=json_body,).parsed


async def asyncio_detailed(
    *, client: Client, json_body: TextClassificationRecordsBulk,
) -> Response[Union[BulkResponse, HTTPValidationError]]:
    kwargs = _get_kwargs(client=client, json_body=json_body,)

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *, client: Client, json_body: TextClassificationRecordsBulk,
) -> Optional[Union[BulkResponse, HTTPValidationError]]:
    """  """

    return (await asyncio_detailed(client=client, json_body=json_body,)).parsed
