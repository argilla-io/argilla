"""
Common environment vars / settings
"""
from typing import List

from pydantic import BaseSettings


class ApiSettings(BaseSettings):
    """
    Main api settings. The pydantic BaseSettings class makes
    accessible environment variables by setting attributes.

    See <https://pydantic-docs.helpmanual.io/usage/settings/>

    only_bulk_api: (ONLY_BULK_API env var)
         If True, activate only bulk and search endpoints

    elasticseach: (ELASTICSEARCH env var)
        The elasticsearch endpoint for datasets persistence

    cors_origins: (CORS_ORIGINS env var)
        List of host patterns for CORS origin access

    docs_enabled: True
        If True, enable openapi docs endpoint at /api/docs

    es_records_index_shards:
        Configures the number of shards for dataset records index creation. Default=1

    es_records_index_replicas:
        Configures the number of shard replicas for dataset records index creation. Default=0
    """

    only_bulk_api: bool = False
    elasticsearch: str = "http://localhost:9200"
    cors_origins: List[str] = ["*"]

    docs_enabled: bool = True

    es_records_index_shards: int = 1
    es_records_index_replicas: int = 0


settings = ApiSettings()
