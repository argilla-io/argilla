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

from types import TracebackType
from typing import Any, ContextManager, Dict, Optional, Type

from packaging.version import parse

from argilla.client.apis import AbstractApi
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.errors import ApiCompatibilityError
from argilla.pydantic_v1 import BaseModel


class ApiInfo(BaseModel):
    version: Optional[str] = None


class ElasticSearchVersionDetails(BaseModel):
    distribution: Optional[str] = None
    number: str
    build_flavor: Optional[str] = None
    build_type: str
    build_hash: str
    build_date: str
    build_snapshot: bool
    lucene_version: str
    minimum_wire_compatibility_version: str
    minimum_index_compatibility_version: str


class ElasticSearch(BaseModel):
    name: str
    cluster_name: str
    cluster_uuid: str
    version: ElasticSearchVersionDetails
    tagline: str


class ApiStatus(BaseModel):
    version: str
    elasticsearch: ElasticSearch
    mem_info: Dict[str, Any]


class Status(AbstractApi):
    def get_info(self) -> ApiInfo:
        """
        Get the connected API info

        Returns:
            ApiInfo: The API info
        """

        response = self.http_client.get("/api/_info")
        return ApiInfo.parse_obj(response)

    def get_status(self) -> ApiStatus:
        response = self.http_client.get("/api/_status")
        return ApiStatus.parse_obj(response)


class _ApiCompatibilityContextManager(ContextManager):
    def __init__(
        self,
        client: AuthenticatedClient,
        min_version: str,
    ):
        self._min_version = parse(min_version)
        self._status_api = Status(client=client) if client else None

    def __enter__(self):
        if self._status_api:
            api_info = self._status_api.get_info()
            api_version = api_info.version

            api_version = parse(api_version)
            if api_version.is_devrelease:
                api_version = parse(api_version.base_version)
            if not api_version >= self._min_version:
                raise ApiCompatibilityError(str(self._min_version), api_version=api_version)
        pass

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        pass


def api_compatibility(api: AbstractApi, min_version: str):
    """
    Handles problems related to server API compatibility.

    Args:
        api: The api component where apply the api compatibility
        min_version: the minimal version that the argilla client can work with
    """
    return _ApiCompatibilityContextManager(
        min_version=min_version,
        client=api.http_client,
    )
