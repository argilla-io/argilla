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

from typing import Any, Dict, Iterable, List, Optional, Tuple

from pydantic import BaseModel, Field

from argilla.logging import LoggingMixin
from argilla.server.commons.models import TaskType
from argilla.server.daos.backend.base import IndexNotFoundError, InvalidSearchError
from argilla.server.daos.backend.client_adapters.base import IClientAdapter
from argilla.server.daos.backend.client_adapters.factory import ClientAdapterFactory
from argilla.server.daos.backend.mappings.datasets import (
    DATASETS_INDEX_NAME,
    datasets_index_mappings,
)
from argilla.server.daos.backend.mappings.helpers import (
    mappings,
    tasks_common_mappings,
    tasks_common_settings,
)
from argilla.server.daos.backend.mappings.text2text import text2text_mappings
from argilla.server.daos.backend.mappings.text_classification import (
    text_classification_mappings,
)
from argilla.server.daos.backend.mappings.token_classification import (
    token_classification_mappings,
)
from argilla.server.daos.backend.metrics import ALL_METRICS
from argilla.server.daos.backend.metrics.base import ElasticsearchMetric
from argilla.server.daos.backend.search.model import (
    BackendRecordsQuery,
    BaseDatasetsQuery,
    BaseQuery,
    BaseRecordsQuery,
    SortableField,
    SortConfig,
)
from argilla.server.errors import BadRequestError, EntityNotFoundError
from argilla.server.errors.task_errors import MetadataLimitExceededError
from argilla.server.settings import settings

NON_SEARCHABLE_PREFIX = "_"


def dataset_records_index(dataset_id: str) -> str:
    index_mame_template = settings.dataset_records_index_name
    return index_mame_template.format(dataset_id)


class PaginatedSortInfo(BaseModel):
    shuffle: bool = False
    sort_by: List[SortableField] = Field(default_factory=list)
    next_search_params: Optional[Any] = None


class GenericElasticEngineBackend(LoggingMixin):
    """
    Encapsulates logic about the communication, queries and index mapping
    transformations between DAOs layer and the elasticsearch backend.
    """

    _INSTANCE = None

    # TODO(@frascuchon): Once id is included as keyword in datasets index, we can discard this
    __MAX_NUMBER_OF_LISTED_DATASETS__ = 2500

    @classmethod
    def get_instance(cls) -> "GenericElasticEngineBackend":
        """
        Creates an instance of ElasticsearchBackend.

        This function is used in fastapi for resolve component dependencies.

        See <https://fastapi.tiangolo.com/tutorial/dependencies/>

        Returns
        -------

        """

        if not cls._INSTANCE:
            instance = cls(
                client=ClientAdapterFactory.get(
                    hosts=settings.elasticsearch,
                    index_shards=settings.es_records_index_shards,
                    ssl_verify=settings.elasticsearch_ssl_verify,
                    ca_path=settings.elasticsearch_ca_path,
                ),
                metrics={**ALL_METRICS},
                mappings={
                    TaskType.text_classification: text_classification_mappings(),
                    TaskType.token_classification: token_classification_mappings(),
                    TaskType.text2text: text2text_mappings(),
                },
            )
            cls._INSTANCE = instance

        return cls._INSTANCE

    def __init__(
        self,
        client: IClientAdapter,
        metrics: Dict[str, ElasticsearchMetric] = None,
        mappings: Dict[str, Dict[str, Any]] = None,
    ):
        self.__client__ = client
        self.__defined_metrics__ = metrics or {}
        self.__tasks_mappings__ = mappings

        self._common_records_mappings = tasks_common_mappings()
        self._common_records_settings = tasks_common_settings()

    @property
    def client(self) -> IClientAdapter:
        """The elasticsearch client"""
        return self.__client__

    def find_metric_by_id(self, metric_id: str) -> Optional[ElasticsearchMetric]:
        metric = self.__defined_metrics__.get(metric_id)
        if not metric:
            raise EntityNotFoundError(
                name=metric_id,
                type=ElasticsearchMetric,
            )
        return metric

    def get_task_mapping(self, task: TaskType) -> Dict[str, Any]:
        return self.__tasks_mappings__[task]

    def compute_metric(
        self,
        id: str,
        metric_id: str,
        query: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        index = dataset_records_index(id)
        return self._compute_metric(
            index=index,
            metric_id=metric_id,
            query=query,
            params=params,
        )

    def get_schema(self, id: str) -> Dict[str, Any]:
        index = dataset_records_index(id)
        return self.client.get_index_schema(index=index)

    async def update_records_content(
        self,
        id: str,
        content: Dict[str, Any],
        query: Optional[BaseDatasetsQuery],
    ) -> Tuple[int, int]:
        index = dataset_records_index(id)
        response = self.client.update_docs_by_query(
            index=index,
            data=content,
            query=query,
        )
        total, updated = response["total"], response["updated"]
        return total, updated

    async def delete_records_by_query(
        self,
        id: str,
        query: Optional[BaseDatasetsQuery],
    ) -> Tuple[int, int]:
        index = dataset_records_index(id)
        total, deleted = self.client.delete_docs_by_query(
            index=index,
            query=query,
        )
        return total, deleted

    def search_records(
        self,
        id: str,
        query: BackendRecordsQuery = BaseRecordsQuery(),
        sort: SortConfig = SortConfig(),
        record_from: int = 0,
        size: int = 100,
        exclude_fields: List[str] = None,
        enable_highlight: bool = True,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        index = dataset_records_index(id)

        if not sort.sort_by and sort.shuffle is False:
            sort.sort_by = [SortableField(id="id")]  # Default sort by id

        results = self.client.search_docs(
            index=index,
            query=query,
            sort=sort,
            doc_from=record_from,
            size=size,
            exclude_fields=exclude_fields,
            enable_highlight=enable_highlight,
        )

        total = results["total"]
        records = results["docs"]

        return total, records

    def scan_records(
        self,
        id: str,
        query: BackendRecordsQuery,
        sort: PaginatedSortInfo,
        limit: Optional[int] = None,
        include_fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
    ) -> Iterable[Dict[str, Any]]:
        index = dataset_records_index(id)

        yield from self.client.scan_docs(
            index=index,
            query=query,
            sort=SortConfig(shuffle=sort.shuffle, sort_by=sort.sort_by),
            size=limit,
            search_from_params=sort.next_search_params,
            fetch_once=sort.shuffle,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            enable_highlight=True,
        )

    def open(self, id: str):
        self.client.open_index(dataset_records_index(id))

    def create_dataset(
        self,
        id: str,
        task: TaskType,
        metadata_values: Optional[Dict[str, Any]] = None,
        vectors_cfg: Optional[Dict[str, Any]] = None,
        force_recreate: bool = False,
    ) -> None:
        _mappings = self._common_records_mappings
        task_mappings = self.get_task_mapping(task).copy()
        for k in task_mappings:
            if isinstance(task_mappings[k], list):
                _mappings[k] = [*_mappings.get(k, []), *task_mappings[k]]
            else:
                _mappings[k] = {**_mappings.get(k, {}), **task_mappings[k]}

        index = dataset_records_index(id)
        self.client.create_index(
            index=index,
            settings=self._common_records_settings,
            mappings={**self._common_records_mappings, **_mappings},
            force_recreate=force_recreate,
        )
        if metadata_values:
            self._configure_metadata_fields(
                index=index,
                metadata_values=metadata_values,
            )

        if vectors_cfg:
            self._configure_vectors_fields(
                index=index,
                vectors_cfg=vectors_cfg,
            )

    def _configure_vectors_fields(
        self,
        index: str,
        vectors_cfg: dict,
    ):
        def _check_max_number_of_vectors():
            vectors = self.client.get_property_type(
                index=index,
                property_name="vectors",
                drop_extra_props=True,
            )
            vector_names = {key for key in vectors.keys() if "vector" in vectors[key]}
            for key in vectors_cfg.keys():
                vector_names.add(f"vectors.{key}.value")

            if len(vector_names) > settings.vectors_fields_limit:
                raise BadRequestError(
                    detail=f"Cannot create more than {settings.vectors_fields_limit} " "kind of vectors per dataset"
                )

        _check_max_number_of_vectors()

        self.client.configure_index_vectors(
            index=index,
            vectors=vectors_cfg,
        )

    def _configure_metadata_fields(self, index: str, metadata_values: Dict[str, Any]):
        def check_metadata_length(metadata_length: int = 0):
            if metadata_length > settings.metadata_fields_limit:
                raise MetadataLimitExceededError(
                    length=metadata_length,
                    limit=settings.metadata_fields_limit,
                )

        def detect_nested_type(v: Any) -> bool:
            """Returns True if value match as nested value"""
            return isinstance(v, list) and isinstance(v[0], dict)

        check_metadata_length(len(metadata_values))
        check_metadata_length(
            len(
                {
                    *self.client.get_property_type(
                        index=index,
                        property_name="metadata",
                        drop_extra_props=True,
                    ),
                    *[f"metadata.{k}" for k in metadata_values.keys()],
                }
            )
        )

        index_mappings = {}
        for field, value in metadata_values.items():
            if field.startswith(NON_SEARCHABLE_PREFIX):
                index_mappings[f"metadata.{field}"] = mappings.non_searchable_text_field()
            elif detect_nested_type(value):
                index_mappings[f"metadata.{field}"] = mappings.nested_field()

        self.client.set_index_mappings(index, properties=index_mappings)

    def delete(self, id: str):
        index = dataset_records_index(id)
        try:
            self.client.delete_index(
                index=index,
                raises_error=True,
            )
        except InvalidSearchError:
            # It's an alias --> DELETE from original index
            original_index = self._old_dataset_index(id)
            self.client.delete_index_alias(
                index=original_index,
                alias=index,
            )
        finally:
            # TODO: This should be move to the service layer and drop from datasets
            self.client.delete_index_document(
                index=DATASETS_INDEX_NAME,
                id=id,
            )

    def _old_dataset_index(self, id):
        return settings.old_dataset_records_index_name.format(id)

    def copy(self, id_from: str, id_to: str):
        index_from = dataset_records_index(id_from)
        index_to = dataset_records_index(id_to)

        self.client.copy_index(
            source_index=index_from,
            target_index=index_to,
        )

    def close(self, id: str):
        return self.client.close_index(index=dataset_records_index(id))

    def create_datasets_index(self, force_recreate: bool = False):
        self.client.create_index(
            index=DATASETS_INDEX_NAME,
            force_recreate=force_recreate,
            mappings=datasets_index_mappings(),
        )
        # TODO: Remove this section of code
        if settings.enable_migration:
            try:
                self._migrate_from_rubrix()
            except IndexNotFoundError:
                pass  # Nothing to migrate

    def _migrate_from_rubrix(self):
        source_index = settings.old_dataset_index_name
        target_index = DATASETS_INDEX_NAME

        try:
            self.client.copy_index(
                source_index=source_index,
                target_index=target_index,
                reindex=True,
            )
            for doc in self.client.scan_docs(index=source_index, query=BaseQuery(), sort=SortConfig()):
                dataset_id = doc["id"]
                index = self._old_dataset_index(dataset_id)
                alias = dataset_records_index(dataset_id=dataset_id)
                self._update_dynamic_mapping(index)
                self.client.create_index_alias(
                    index=index,
                    alias=alias,
                )
        except IndexNotFoundError:
            pass  # Nothing to migrate

    def _update_dynamic_mapping(self, index: str):
        self.client.set_index_mappings(
            index=index,
            dynamic=False,
        )

    def list_datasets(self, query: BaseDatasetsQuery):
        return self.client.scan_docs(
            index=DATASETS_INDEX_NAME,
            query=query,
            sort=SortConfig(),
            fetch_once=True,
            size=self.__MAX_NUMBER_OF_LISTED_DATASETS__,
        )

    def find_record_by_id(self, dataset_id: str, record_id: str):
        index = dataset_records_index(dataset_id)
        return self.client.get_index_document_by_id(
            index=index,
            id=record_id,
        )

    def add_dataset_document(
        self,
        id: str,
        document: Dict[str, Any],
    ):
        self.client.upsert_index_document(
            index=DATASETS_INDEX_NAME,
            id=id,
            document=document,
        )

    def update_dataset_document(
        self,
        id: str,
        document: Dict[str, Any],
    ):
        self.client.upsert_index_document(
            index=DATASETS_INDEX_NAME,
            id=id,
            document=document,
            partial_update=True,
        )

    def update_record(
        self,
        dataset_id: str,
        record_id: str,
        content: dict,
    ):
        index = dataset_records_index(dataset_id)
        self.client.upsert_index_document(
            index=index,
            id=record_id,
            document=content,
        )

    def find_dataset(
        self,
        id: str,
    ):
        document = self.client.get_index_document_by_id(
            index=DATASETS_INDEX_NAME,
            id=id,
        )
        return document

    def _compute_metric(
        self,
        index: str,
        metric_id: str,
        query: Optional[BaseQuery] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        metric = self.find_metric_by_id(metric_id)
        data = self.client.compute_index_metric(
            index=index,
            metric=metric,
            query=query,
            params=params or {},
        )
        return data

    def remove_dataset_field(self, id: str, field: str):
        self.client.drop_document_property(
            index=DATASETS_INDEX_NAME,
            id=id,
            property=field,
        )

    def add_dataset_records(self, id: str, documents: List[dict]) -> int:
        index = dataset_records_index(id)

        return self.client.index_documents(index=index, docs=documents)
