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

import dataclasses
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from argilla.server.daos.backend.metrics.base import ElasticsearchMetric
from argilla.server.daos.backend.search.model import BaseQuery, SortConfig


@dataclasses.dataclass
class IClientAdapter(metaclass=ABCMeta):
    vector_search_supported: bool

    @abstractmethod
    def get_cluster_info(self) -> Dict[str, Any]:
        """Returns basic about es cluster"""
        pass

    @abstractmethod
    def get_index_schema(self, *, index: str):
        pass

    @abstractmethod
    def drop_document_property(
        self,
        index: str,
        id: str,
        property: str,
    ):
        pass

    @abstractmethod
    def update_docs_by_query(
        self,
        *,
        index: str,
        data: Dict[str, Any],
        query: Optional[BaseQuery] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_docs_by_query(
        self,
        *,
        index: str,
        query: Optional[BaseQuery],
    ) -> Tuple[int, int]:
        pass

    @abstractmethod
    def scan_docs(
        self,
        index: str,
        query: BaseQuery,
        sort: SortConfig,
        size: Optional[int] = None,
        fetch_once: bool = False,
        search_from_params: Optional[Any] = None,
        enable_highlight: bool = False,
        include_fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
    ) -> Iterable[Dict[str, Any]]:
        pass

    @abstractmethod
    def search_docs(
        self,
        *,
        index: str,
        query: Optional[BaseQuery] = None,
        sort: Optional[SortConfig] = None,
        doc_from: int = 0,
        size: int = 100,
        exclude_fields: List[str] = None,
        enable_highlight: bool = True,
        routing: str = None,
    ):
        pass

    @abstractmethod
    def copy_index(
        self,
        *,
        source_index: str,
        target_index: str,
        override: bool = True,
        reindex: bool = False,
    ):
        pass

    @abstractmethod
    def get_property_type(
        self,
        *,
        index: str,
        property_name: str,
        drop_extra_props: bool = False,
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_index_document_by_id(
        self,
        index: str,
        id: str,
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_index_alias(
        self,
        *,
        index: str,
        alias: str,
    ):
        pass

    @abstractmethod
    def delete_index_document(
        self,
        index: str,
        id: str,
    ):
        pass

    @abstractmethod
    def delete_index_alias(
        self,
        *,
        index: str,
        alias: str,
    ):
        pass

    @abstractmethod
    def exists_index(self, index: str) -> bool:
        pass

    @abstractmethod
    def configure_index_vectors(
        self,
        *,
        index: str,
        vectors: Dict[str, int],
    ):
        pass

    @abstractmethod
    def delete_index(
        self,
        *,
        index: str,
        raises_error: bool = False,
    ):
        pass

    @abstractmethod
    def create_index(
        self,
        index: str,
        force_recreate: bool = False,
        settings: Dict[str, Any] = None,
        mappings: Dict[str, Any] = None,
    ):
        pass

    @abstractmethod
    def index_documents(self, index: str, docs: List[Dict[str, Any]]) -> int:
        pass

    @abstractmethod
    def upsert_index_document(
        self,
        index: str,
        id: str,
        document: Optional[Dict[str, Any]] = None,
        script: Optional[str] = None,
        partial_update: bool = False,
    ):
        pass

    @abstractmethod
    def open_index(self, index: str):
        pass

    @abstractmethod
    def close_index(self, index: str):
        pass

    @abstractmethod
    def clone_index(
        self,
        source_index: str,
        target_index: str,
    ):
        pass

    @abstractmethod
    def set_index_mappings(
        self,
        index: str,
        properties: Optional[Dict[str, Any]] = None,
        **extra_cfg,
    ):
        pass

    @abstractmethod
    def compute_index_metric(
        self,
        *,
        index: str,
        metric: ElasticsearchMetric,
        query: BaseQuery,
        params: Dict[str, Any],
    ):
        pass
