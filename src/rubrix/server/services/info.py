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

import os
from typing import Any, Dict

import psutil
from fastapi import Depends

# TODO(@frascuchon): Remove this dep
from hurry.filesize import size
from pydantic import BaseModel

from rubrix import __version__ as rubrix_version
from rubrix.server.daos.backend.elasticsearch import ElasticsearchBackend


class ApiInfo(BaseModel):
    """Basic api info"""

    rubrix_version: str


class ApiStatus(ApiInfo):
    """The Rubrix api status model"""

    elasticsearch: Dict[str, Any]
    mem_info: Dict[str, Any]


class ApiInfoService:
    """
    The api info service
    """

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        es_wrapper: ElasticsearchBackend = Depends(ElasticsearchBackend.get_instance),
    ) -> "ApiInfoService":
        """
        Creates an api info service
        """

        if not cls._INSTANCE:
            cls._INSTANCE = ApiInfoService(es_wrapper)
        return cls._INSTANCE

    def __init__(self, es: ElasticsearchBackend):
        self.__es__ = es

    def api_status(self) -> ApiStatus:
        """Returns the current api status"""
        return ApiStatus(
            rubrix_version=str(rubrix_version),
            elasticsearch=self._elasticsearch_info(),
            mem_info=self._api_memory_info(),
        )

    def _elasticsearch_info(self) -> Dict[str, Any]:
        """Returns the elasticsearch cluster info"""
        return self.__es__.get_cluster_info()

    @staticmethod
    def _api_memory_info() -> Dict[str, Any]:
        """Fetch the api process memory usage"""
        process = psutil.Process(os.getpid())
        return {k: size(v) for k, v in process.memory_info()._asdict().items()}
