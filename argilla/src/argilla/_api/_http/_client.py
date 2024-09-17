# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass

import httpx


@dataclass
class HTTPClientConfig:
    """Basic configuration for the HTTP client."""

    api_url: str
    api_key: str
    timeout: int = 60
    retries: int = 5


def create_http_client(api_url: str, api_key: str, **client_args) -> httpx.Client:
    """Initialize the SDK with the given API URL and API key."""
    # This piece of code is needed to make old sdk works in combination with new one

    headers = client_args.pop("headers", {})
    headers["X-Argilla-Api-Key"] = api_key
    retries = client_args.pop("retries", 0)

    return httpx.Client(
        base_url=api_url,
        headers=headers,
        transport=httpx.HTTPTransport(retries=retries),
        **client_args,
    )
