#  coding=utf-8
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
import json
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import httpx

from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.errors import GenericApiError
from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import BulkResponse, ErrorMessage, HTTPValidationError, Response
from argilla.client.sdk.text2text.models import Text2TextBulkData
from argilla.client.sdk.text_classification.models import TextClassificationBulkData
from argilla.client.sdk.token_classification.models import TokenClassificationBulkData

_TASK_TO_ENDPOINT = {
    TextClassificationBulkData: "TextClassification",
    TokenClassificationBulkData: "TokenClassification",
    Text2TextBulkData: "Text2Text",
}


def bulk(
    client: AuthenticatedClient,
    name: str,
    json_body: Union[TextClassificationBulkData, TokenClassificationBulkData, Text2TextBulkData],
) -> BulkResponse:
    url = f"{client.base_url}/api/datasets/{name}/{_TASK_TO_ENDPOINT[type(json_body)]}:bulk"

    response = client.post(path=url, json=json_body.dict(by_alias=True))
    return BulkResponse.parse_obj(response)


T = TypeVar("T")


def build_list_response(
    response: httpx.Response, item_class: Type[T]
) -> Response[Union[List[T], HTTPValidationError, ErrorMessage]]:
    parsed_response = response.json()

    if 200 <= response.status_code < 400:
        parsed_response = [item_class(**r) for r in parsed_response]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )

    return handle_response_error(response, item_class=item_class)
