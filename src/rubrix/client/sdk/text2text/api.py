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
from typing import List, Optional, Union

import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.api import build_data_response
from rubrix.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from rubrix.client.sdk.text2text.models import Text2TextQuery, Text2TextRecord


def data(
    client: AuthenticatedClient,
    name: str,
    request: Optional[Text2TextQuery] = None,
    limit: Optional[int] = None,
) -> Response[Union[List[Text2TextRecord], HTTPValidationError, ErrorMessage]]:
    url = "{}/api/datasets/{name}/Text2Text/data".format(client.base_url, name=name)

    with httpx.stream(
        method="POST",
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=None,
        params={"limit": limit} if limit else None,
        json=request.dict() if request else {},
    ) as response:
        return build_data_response(response=response, data_type=Text2TextRecord)
