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

from typing import Dict, TypeVar

import httpx
from pydantic import BaseModel, Field

from rubrix._constants import API_KEY_HEADER_NAME
from rubrix.client.sdk._helpers import build_raw_response


class Client(BaseModel):
    base_url: str
    cookies: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout: float = 5.0

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in all endpoints"""
        return {**self.headers}

    def get_cookies(self) -> Dict[str, str]:
        return {**self.cookies}

    def get_timeout(self) -> float:
        return self.timeout


ResponseType = TypeVar("ResponseType")


class AuthenticatedClient(Client):
    """A Client which has been authenticated for use on secured endpoints"""

    token: str

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints"""
        return {
            "Authorization": f"Bearer {self.token}",  # Backward compatibility
            API_KEY_HEADER_NAME: self.token,
            **super().get_headers(),
        }

    def __hash__(self):
        return hash((self.base_url, self.token))

    def get(self, path: str, *args, **kwargs):
        url = f"{self.base_url}/{path}"
        response = httpx.get(
            url=url,
            headers=self.get_headers(),
            cookies=self.get_cookies(),
            timeout=self.get_timeout(),
            *args,
            **kwargs,
        )

        return build_raw_response(response).parsed

    def post(self, path: str, *args, **kwargs):
        url = f"{self.base_url}/{path}"

        response = httpx.post(
            url=url,
            headers=self.get_headers(),
            cookies=self.get_cookies(),
            timeout=self.get_timeout(),
            *args,
            **kwargs,
        )
        return build_raw_response(response)

    def put(self, path: str, *args, **kwargs):
        url = f"{self.base_url}/{path}"

        response = httpx.put(
            url=url,
            headers=self.get_headers(),
            cookies=self.get_cookies(),
            timeout=self.get_timeout(),
            *args,
            **kwargs,
        )
        return build_raw_response(response)
