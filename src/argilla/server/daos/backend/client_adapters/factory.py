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
import logging
from typing import Tuple, Type, Union

from opensearchpy import (
    ConnectionError as OpenSearchConnectionError,
)
from opensearchpy import (
    NotFoundError as OpenSearchNotFoundError,
)
from opensearchpy import (
    OpenSearch,
)
from opensearchpy import (
    RequestError as OpenSearchRequestError,
)
from packaging.version import parse

from argilla.server.daos.backend.base import GenericSearchError
from argilla.server.daos.backend.client_adapters import (
    ElasticsearchClient,
    IClientAdapter,
    OpenSearchClient,
)
from argilla.server.daos.backend.client_adapters.elasticsearch import (
    ApiError as ElasticSearchApiError,
)
from argilla.server.daos.backend.client_adapters.elasticsearch import (
    ConnectionError as ElasticConnectionError,
)
from argilla.server.daos.backend.client_adapters.elasticsearch import (
    Elasticsearch,
)
from argilla.server.settings import settings

ELASTICSEARCH_DISTRIBUTION = "elasticsearch"
OPENSEARCH_DISTRIBUTION = "opensearch"

_DEFAULT_DISTRIBUTION = OPENSEARCH_DISTRIBUTION
_DEFAULT_VERSION = "2.0"

_LOGGER = logging.getLogger("argilla")


class ClientAdapterFactory:
    @classmethod
    def get(cls) -> IClientAdapter:
        client_config = dict(
            hosts=settings.elasticsearch,
            verify_certs=settings.elasticsearch_ssl_verify,
            ca_certs=settings.elasticsearch_ca_path,
            retry_on_timeout=True,
            max_retries=5,
        )

        if settings.elasticsearch_extra_args:
            client_config.update(settings.elasticsearch_extra_args)
            client = Elasticsearch(**client_config)
        else:
            # See here https://opensearch.org/docs/latest/clients/index/#legacy-clients
            client_config.update(settings.opensearch_extra_args)
            client = OpenSearch(**client_config)

        distribution, version = cls._fetch_cluster_version_info(client)
        client.close()

        (adapter_class, support_vector_search) = cls._resolve_adapter_class_with_vector_support(version, distribution)

        return adapter_class(
            index_shards=settings.es_records_index_shards,
            vector_search_supported=support_vector_search,
            config_backend=client_config,
        )

    @classmethod
    def _resolve_adapter_class_with_vector_support(cls, version: str, distribution: str) -> Tuple[Type, bool]:
        support_vector_search = True

        if distribution == ELASTICSEARCH_DISTRIBUTION and parse("8.5") <= parse(version):
            if parse("8.5") <= parse(ElasticsearchClient.ES_CLIENT_VERSION):
                adapter_class = ElasticsearchClient
            else:
                _LOGGER.warning(
                    "Elasticsearch 8.5 backend found but installed\n"
                    "client does not support vectors. Please upgrade your elasticsearch client\n"
                    "if you want to support similarity search in argilla."
                )
                adapter_class = OpenSearchClient
                support_vector_search = False
        elif distribution == OPENSEARCH_DISTRIBUTION and parse("2.2") <= parse(version):
            adapter_class = OpenSearchClient
        else:
            adapter_class = OpenSearchClient
            support_vector_search = False

        return adapter_class, support_vector_search

    @classmethod
    def _fetch_cluster_version_info(cls, client: Union[Elasticsearch, OpenSearch]) -> Tuple[str, str]:
        try:
            data = client.info()

            version_info = data["version"]
            version: str = version_info["number"]
            distribution: str = version_info.get("distribution", "elasticsearch")

            return distribution, version
        except (ElasticSearchApiError, OpenSearchNotFoundError, OpenSearchRequestError) as error:
            default = (_DEFAULT_DISTRIBUTION, _DEFAULT_VERSION)
            _LOGGER.warning(
                f"Cannot identify version and distribution from connected backend. Error: {error}.\n"
                f"Using default one: {default!r}"
            )
            return default
        except Exception as error:
            raise GenericSearchError(error)
