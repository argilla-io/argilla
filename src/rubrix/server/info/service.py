import os
from typing import Any, Dict, Optional

import psutil
from elasticsearch import Elasticsearch, ElasticsearchException
from fastapi import Depends
from hurry.filesize import size
from rubrix import __version__ as rubrix_version
from rubrix.server.commons.es_wrapper import ElasticsearchWrapper, create_es_wrapper

from .model import ApiStatus


class ApiInfoService:
    """
    The api info service
    """

    def __init__(self, es: Elasticsearch):
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
        try:
            return self.__es__.info()
        except ElasticsearchException as ex:
            return {"error": ex}

    @staticmethod
    def _api_memory_info() -> Dict[str, Any]:
        """Fetch the api process memory usage"""
        process = psutil.Process(os.getpid())
        return {k: size(v) for k, v in process.memory_info()._asdict().items()}


_instance: Optional[ApiInfoService] = None


def create_info_service(
    es_wrapper: ElasticsearchWrapper = Depends(create_es_wrapper),
) -> ApiInfoService:
    """
    Creates an api info service
    """

    global _instance
    if not _instance:
        _instance = ApiInfoService(es_wrapper.client)
    return _instance
