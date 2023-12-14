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

from typing import Optional

import httpx

from ._api import HTTPClientConfig
from ._datasets import Dataset
from ._models import *

from argilla.client.workspaces import Workspace # noqa

default_http_client: Optional[httpx.Client] = None


def _set_default_http_client(client: httpx.Client) -> None:
    global default_http_client

    default_http_client = client


def init(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 60,
    **client_args,
) -> None:
    """Initialize the SDK with the given API URL and API key."""
    # This piece of code is needed to make old sdk works in combination with new one
    import argilla as rg

    rg.init(api_url, api_key, timeout=timeout)

    config = HTTPClientConfig()

    api_url = api_url or config.api_url
    api_key = api_key or config.api_key

    headers = client_args.pop("headers", {})
    headers["X-Argilla-Api-Key"] = api_key

    client = httpx.Client(base_url=api_url, timeout=timeout, headers=headers, **client_args)
    _set_default_http_client(client)
