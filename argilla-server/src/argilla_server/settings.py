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
import re
import warnings
from pathlib import Path
from typing import Dict, List, Optional

from argilla_server.constants import (
    DATABASE_POSTGRESQL,
    DATABASE_SQLITE,
    DEFAULT_DATABASE_POSTGRESQL_MAX_OVERFLOW,
    DEFAULT_DATABASE_POSTGRESQL_POOL_SIZE,
    DEFAULT_DATABASE_SQLITE_TIMEOUT,
    DEFAULT_LABEL_SELECTION_OPTIONS_MAX_ITEMS,
    DEFAULT_SPAN_OPTIONS_MAX_ITEMS,
    SEARCH_ENGINE_ELASTICSEARCH,
    SEARCH_ENGINE_OPENSEARCH,
)
from argilla_server.pydantic_v1 import BaseSettings, Field, root_validator, validator


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
    # https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine.params.pool_size
    database_postgresql_pool_size: Optional[int] = Field(
        default=DEFAULT_DATABASE_POSTGRESQL_POOL_SIZE,
        description="The number of connections to keep open inside the database connection pool",
    )
    # https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine.params.max_overflow
    database_postgresql_max_overflow: Optional[int] = Field(
        default=DEFAULT_DATABASE_POSTGRESQL_MAX_OVERFLOW,
        description="The number of connections that can be opened above and beyond the pool_size setting",
    )
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
    database_sqlite_timeout: Optional[int] = Field(
        default=DEFAULT_DATABASE_SQLITE_TIMEOUT,
        description="SQLite database connection timeout in seconds",
    )

    elasticsearch: str = "http://localhost:9200"
    elasticsearch_ssl_verify: bool = True
    elasticsearch_ca_path: Optional[str] = None
    cors_origins: List[str] = ["*"]

    redis_url: str = "redis://localhost:6379/0"

    docs_enabled: bool = True

    # Analyzer configuration
    es_records_index_shards: int = 1
    es_records_index_replicas: int = 0

    es_mapping_total_fields_limit: int = 2000

    search_engine: str = SEARCH_ENGINE_ELASTICSEARCH

    # Questions settings
    label_selection_options_max_items: int = Field(
        default=DEFAULT_LABEL_SELECTION_OPTIONS_MAX_ITEMS,
        description="Max number of label options for questions of type `label_selection` and `multi_label_selection`",
    )

    span_options_max_items: int = Field(
        default=DEFAULT_SPAN_OPTIONS_MAX_ITEMS,
        description="Max number of label options for questions of type `span`",
    )

    # Hugging Face settings
    show_huggingface_space_persistent_storage_warning: bool = Field(
        default=True,
        description="If True, show a warning when Hugging Face space persistent storage is disabled",
    )

    # Hugging Face telemetry
    enable_telemetry: bool = Field(
        default=True, description="The telemetry configuration for Hugging Face hub telemetry. "
    )

    # See also the telemetry.py module
    @validator("enable_telemetry", pre=True, always=True)
    def set_enable_telemetry(cls, enable_telemetry: bool) -> bool:
        if os.getenv("HF_HUB_DISABLE_TELEMETRY") == "1" or os.getenv("HF_HUB_OFFLINE") == "1":
            enable_telemetry = False
        if os.getenv("ARGILLA_ENABLE_TELEMETRY") == "0":
            os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
            warnings.warn(
                "environment vairbale ARGILLA_ENABLE_TELEMETRY is deprecated, use HF_HUB_DISABLE_TELEMETRY or HF_HUB_OFFLINE instead."
            )
            enable_telemetry = False

        return enable_telemetry

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

    @validator("database_url", pre=True, always=True)
    def set_database_url(cls, database_url: str, values: dict) -> str:
        if not database_url:
            home_path = values.get("home_path")
            sqlite_file = os.path.join(home_path, "argilla.db")
            return f"sqlite+aiosqlite:///{sqlite_file}"

        if "sqlite" in database_url:
            regex = re.compile(r"sqlite(?!\+aiosqlite)")
            if regex.match(database_url):
                warnings.warn(
                    "From version 1.14.0, Argilla will use `aiosqlite` as default SQLite driver. The protocol in the"
                    " provided database URL has been automatically replaced from `sqlite` to `sqlite+aiosqlite`."
                    " Please, update your database URL to use `sqlite+aiosqlite` protocol."
                )
                return re.sub(regex, "sqlite+aiosqlite", database_url)

        if "postgresql" in database_url:
            regex = re.compile(r"postgresql(?!\+asyncpg)(\+psycopg2)?")
            if regex.match(database_url):
                warnings.warn(
                    "From version 1.14.0, Argilla will use `asyncpg` as default PostgreSQL driver. The protocol in the"
                    " provided database URL has been automatically replaced from `postgresql` to `postgresql+asyncpg`."
                    " Please, update your database URL to use `postgresql+asyncpg` protocol."
                )
                return re.sub(regex, "postgresql+asyncpg", database_url)

        return database_url

    @root_validator(skip_on_failure=True)
    def create_home_path(cls, values):
        Path(values["home_path"]).mkdir(parents=True, exist_ok=True)

        return values

    @property
    def database_engine_args(self) -> Dict:
        if self.database_is_sqlite:
            return {
                "connect_args": {
                    "timeout": self.database_sqlite_timeout,
                },
            }

        if self.database_is_postgresql:
            return {
                "pool_size": self.database_postgresql_pool_size,
                "max_overflow": self.database_postgresql_max_overflow,
            }

        return {}

    @property
    def database_is_sqlite(self) -> bool:
        if self.database_url is None:
            return False

        return self.database_url.lower().startswith(DATABASE_SQLITE)

    @property
    def database_is_postgresql(self) -> bool:
        if self.database_url is None:
            return False

        return self.database_url.lower().startswith(DATABASE_POSTGRESQL)

    @property
    def search_engine_is_elasticsearch(self) -> bool:
        return self.search_engine == SEARCH_ENGINE_ELASTICSEARCH

    @property
    def search_engine_is_opensearch(self) -> bool:
        return self.search_engine == SEARCH_ENGINE_OPENSEARCH

    class Config:
        env_prefix = "ARGILLA_"


settings = Settings()
