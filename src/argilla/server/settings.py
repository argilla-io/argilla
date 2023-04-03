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
import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseSettings, Field, root_validator, validator

from argilla._constants import DEFAULT_MAX_KEYWORD_LENGTH, DEFAULT_TELEMETRY_KEY


class Settings(BaseSettings):
    """
    Main application settings. The pydantic BaseSettings class makes
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

    __DATASETS_INDEX_NAME__ = "ar.datasets"
    __DATASETS_RECORDS_INDEX_NAME__ = "ar.dataset.{}"

    home_path: Optional[str] = Field(description="The home path where argilla related files will be stored")
    base_url: Optional[str] = Field(description="The default base url where server will be deployed")
    database_url: Optional[str] = Field(description="The database url that argilla will use as data store")

    elasticsearch: str = "http://localhost:9200"
    elasticsearch_ssl_verify: bool = True
    elasticsearch_ca_path: Optional[str] = None
    cors_origins: List[str] = ["*"]

    docs_enabled: bool = True

    namespace: str = Field(default=None, regex=r"^[a-z]+$")

    enable_migration: bool = Field(
        default=False,
        description="If enabled, try to migrate data from old rubrix installation",
    )

    # Analyzer configuration
    default_es_search_analyzer: str = "standard"
    exact_es_search_analyzer: str = "whitespace"
    # This line will be enabled once words field won't be used anymore
    # wordcloud_es_search_analyzer: str = "multilingual_stop_analyzer"

    es_records_index_shards: int = 1
    es_records_index_replicas: int = 0

    vectors_fields_limit: int = Field(
        default=5,
        description="Max number of supported vectors per record",
    )

    metadata_fields_limit: int = Field(
        default=50,
        gt=0,
        le=100,
        description="Max number of fields in metadata",
    )
    metadata_field_length: int = Field(
        default=DEFAULT_MAX_KEYWORD_LENGTH,
        description="Max length supported for the string metadata fields."
        " Values containing higher than this will be truncated",
    )

    enable_telemetry: bool = True

    telemetry_key: str = DEFAULT_TELEMETRY_KEY

    @validator("home_path", always=True)
    def set_home_path_default(cls, home_path: str):
        return home_path or os.path.join(Path.home(), ".argilla")

    @validator("base_url", always=True)
    def normalize_base_url(cls, base_url: str):
        if not base_url:
            base_url = "/"
        if not base_url.startswith("/"):
            base_url = "/" + base_url
        if not base_url.endswith("/"):
            base_url += "/"

        return base_url

    @validator("database_url", always=True)
    def set_database_url_default(cls, database_url: str, values: dict):
        return database_url or f"sqlite:///{os.path.join(values['home_path'], 'argilla.db')}?check_same_thread=False"

    @root_validator(skip_on_failure=True)
    def create_home_path(cls, values):
        Path(values["home_path"]).mkdir(parents=True, exist_ok=True)

        return values

    @property
    def dataset_index_name(self) -> str:
        ns = self.namespace
        if ns:
            return f"{self.namespace}.{self.__DATASETS_INDEX_NAME__}"
        return self.__DATASETS_INDEX_NAME__

    @property
    def dataset_records_index_name(self) -> str:
        ns = self.namespace
        if ns:
            return f"{self.namespace}.{self.__DATASETS_RECORDS_INDEX_NAME__}"
        return self.__DATASETS_RECORDS_INDEX_NAME__

    @property
    def old_dataset_index_name(self) -> str:
        index_name = ".rubrix<NAMESPACE>.datasets-v0"
        ns = self.namespace
        if ns is None:
            return index_name.replace("<NAMESPACE>", "")
        return index_name.replace("<NAMESPACE>", f".{ns}")

    @property
    def old_dataset_records_index_name(self) -> str:
        index_name = ".rubrix<NAMESPACE>.dataset.{}.records-v0"
        ns = self.namespace
        if ns is None:
            return index_name.replace("<NAMESPACE>", "")
        return index_name.replace("<NAMESPACE>", f".{ns}")

    def obfuscated_elasticsearch(self) -> str:
        """Returns configured elasticsearch url obfuscating the provided password, if any"""
        parsed = urlparse(self.elasticsearch)
        if parsed.password:
            return self.elasticsearch.replace(parsed.password, "XXXX")
        return self.elasticsearch

    class Config:
        # TODO: include a common prefix for all argilla env vars.
        env_prefix = "ARGILLA_"
        fields = {
            # TODO(@frascuchon): Remove in 0.20.0
            "elasticsearch": {
                "env": ["ELASTICSEARCH", f"{env_prefix}ELASTICSEARCH"],
            },
            "elasticsearch_ssl_verify": {
                "env": [
                    "ELASTICSEARCH_SSL_VERIFY",
                    f"{env_prefix}ELASTICSEARCH_SSL_VERIFY",
                ]
            },
            "cors_origins": {"env": ["CORS_ORIGINS", f"{env_prefix}CORS_ORIGINS"]},
            "docs_enabled": {"env": ["DOCS_ENABLED", f"{env_prefix}DOCS_ENABLED"]},
            "es_records_index_shards": {
                "env": [
                    "ES_RECORDS_INDEX_SHARDS",
                    f"{env_prefix}ES_RECORDS_INDEX_SHARDS",
                ]
            },
            "es_records_index_replicas": {
                "env": [
                    "ES_RECORDS_INDEX_REPLICAS",
                    f"{env_prefix}ES_RECORDS_INDEX_SHARDS",
                ]
            },
        }


settings = Settings()
