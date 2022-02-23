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

"""
Common environment vars / settings
"""
import logging
from typing import List
from urllib.parse import urlparse

from pydantic import BaseSettings, Field, validator


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

    disable_es_index_template_creation: (DISABLE_ES_INDEX_TEMPLATE_CREATION env var)
         Allowing advanced users to create their own es index settings and mappings. Default=False

    """

    __LOGGER__ = logging.getLogger(__name__)

    __DATASETS_INDEX_NAME__ = ".rubrix<NAMESPACE>.datasets-v0"
    __DATASETS_RECORDS_INDEX_NAME__ = ".rubrix<NAMESPACE>.dataset.{}.records-v0"

    elasticsearch: str = "http://localhost:9200"
    elasticsearch_ssl_verify: bool = True
    cors_origins: List[str] = ["*"]

    docs_enabled: bool = True

    namespace: str = Field(default=None, regex=r"^[a-z]+$")

    # Analyzer configuration
    default_es_search_analyzer: str = "standard"
    exact_es_search_analyzer: str = "whitespace"
    # This line will be enabled once words field won't be used anymore
    # wordcloud_es_search_analyzer: str = "multilingual_stop_analyzer"

    es_records_index_shards: int = 1
    es_records_index_replicas: int = 0
    # TODO(@frascuchon): remove in v0.12.0
    disable_es_index_template_creation: bool = False

    metadata_fields_limit: int = Field(
        default=50, gt=0, le=100, description="Max number of fields in metadata"
    )

    @validator("disable_es_index_template_creation", always=True)
    def check_index_template_creation_value(cls, value):

        if value is True:
            cls.__LOGGER__.warning(
                "The environment variable DISABLE_ES_INDEX_TEMPLATE_CREATION won't be used anymore.\n"
                "If you want customize the dataset creation index, please refer documentation "
                "https://rubrix.readthedocs.io/en/stable"
                "/getting_started/advanced_setup_guides.html#change-elasticsearch-index-analyzers"
            )
        return value

    @property
    def dataset_index_name(self) -> str:
        ns = self.namespace
        if ns is None:
            return self.__DATASETS_INDEX_NAME__.replace("<NAMESPACE>", "")
        return self.__DATASETS_INDEX_NAME__.replace("<NAMESPACE>", f".{ns}")

    @property
    def dataset_records_index_name(self) -> str:
        ns = self.namespace
        if ns is None:
            return self.__DATASETS_RECORDS_INDEX_NAME__.replace("<NAMESPACE>", "")
        return self.__DATASETS_RECORDS_INDEX_NAME__.replace("<NAMESPACE>", f".{ns}")

    def obfuscated_elasticsearch(self) -> str:
        """Returns configured elasticsearch url obfuscating the provided password, if any"""
        parsed = urlparse(self.elasticsearch)
        if parsed.password:
            return self.elasticsearch.replace(parsed.password, "XXXX")
        return self.elasticsearch

    class Config:
        # TODO: include a common prefix for all rubrix env vars.
        fields = {
            "elasticsearch_ssl_verify": {
                "env": "RUBRIX_ELASTICSEARCH_SSL_VERIFY",
            },
            "metadata_fields_limit": {"env": "RUBRIX_METADATA_FIELDS_LIMIT"},
            "namespace": {
                "env": "RUBRIX_NAMESPACE",
            },
            "default_es_search_analyzer": {
                "env": "RUBRIX_DEFAULT_ES_SEARCH_ANALYZER",
            },
            "exact_es_search_analyzer": {"env": "RUBRIX_EXACT_ES_SEARCH_ANALYZER"},
        }


settings = ApiSettings()
