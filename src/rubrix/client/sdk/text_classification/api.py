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
from typing import List
from typing import Optional
from typing import Union

import httpx
from rubrix.client.sdk._helpers import build_bulk_response
from rubrix.client.sdk._helpers import build_data_response
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.models import BulkResponse
from rubrix.client.sdk.commons.models import ErrorMessage
from rubrix.client.sdk.commons.models import HTTPValidationError
from rubrix.client.sdk.commons.models import Response
from rubrix.client.sdk.text_classification.models import TextClassificationBulkData
from rubrix.client.sdk.text_classification.models import TextClassificationQuery
from rubrix.client.sdk.text_classification.models import TextClassificationRecord


def bulk(
    client: AuthenticatedClient,
    name: str,
    json_body: TextClassificationBulkData,
) -> Response[Union[BulkResponse, ErrorMessage, HTTPValidationError]]:
    url = "{}/api/datasets/{name}/TextClassification:bulk".format(
        client.base_url, name=name
    )

    response = httpx.post(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        json=json_body.dict(exclude_unset=True),
    )

    return build_bulk_response(response)


def data(
    client: AuthenticatedClient,
    name: str,
    request: Optional[TextClassificationQuery] = None,
    limit: Optional[int] = None,
) -> Response[Union[List[TextClassificationRecord], HTTPValidationError, ErrorMessage]]:
    url = "{}/api/datasets/{name}/TextClassification/data".format(
        client.base_url, name=name
    )

    with httpx.stream(
        "POST",
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=None,
        params={"limit": limit},
        json=request.dict() if request else {},
    ) as response:
        return build_data_response(response=response, data_type=TextClassificationRecord)
