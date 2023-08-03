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

# The following configuration tries to limit use of numpy threading and
# possible problems with fault segmentation
# For more info, please visit https://gist.github.com/EricCousineau-TRI/8a2d1550f5fa4be4fed87d55a522dbf2
import os

from argilla.server.daos.backend.client_adapters.factory import ClientAdapterFactory
from argilla.server.settings import settings

os.environ.update(
    OMP_NUM_THREADS="1",
    OPENBLAS_NUM_THREADS="1",
    NUMEXPR_NUM_THREADS="1",
    MKL_NUM_THREADS="1",
)

try:
    client = ClientAdapterFactory.get(
        hosts=settings.elasticsearch,
        index_shards=settings.es_records_index_shards,
        ssl_verify=settings.elasticsearch_ssl_verify,
        ca_path=settings.elasticsearch_ca_path,
    )

    SUPPORTED_VECTOR_SEARCH = client.vector_search_supported
except Exception:
    SUPPORTED_VECTOR_SEARCH = False
