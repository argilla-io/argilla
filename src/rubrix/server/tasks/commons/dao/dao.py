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

import dataclasses
import datetime
import re
from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar

import deprecated
from fastapi import Depends

from rubrix.server.commons.errors import ClosedDatasetError, MissingDatasetRecordsError
from rubrix.server.commons.es_helpers import aggregations, parse_aggregations
from rubrix.server.commons.es_settings import DATASETS_RECORDS_INDEX_NAME
from rubrix.server.commons.es_wrapper import (
    ClosedIndexError,
    ElasticsearchWrapper,
    IndexNotFoundError,
    create_es_wrapper,
)
from rubrix.server.commons.helpers import unflatten_dict
from rubrix.server.commons.settings import settings
from rubrix.server.datasets.model import BaseDatasetDB
from rubrix.server.tasks.commons import BaseRecord, MetadataLimitExceededError, TaskType
from rubrix.server.tasks.commons.dao.es_config import (
    mappings,
    tasks_common_mappings,
    tasks_common_settings,
)
from rubrix.server.tasks.commons.dao.model import RecordSearch, RecordSearchResults

DBRecord = TypeVar("DBRecord", bound=BaseRecord)


@dataclasses.dataclass
class _IndexTemplateExtensions:

    analyzers: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    properties: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    dynamic_templates: List[Dict[str, Any]] = dataclasses.field(default_factory=list)


_extensions = _IndexTemplateExtensions()


def extends_index_properties(extended_properties: Dict[str, Any]):
    """
    Add explict properties configuration to rubrix index template

    See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html

    Parameters
    ----------
    extended_properties:
        The properties dictionary configuration. Several properties could be configured here

    """
    _extensions.properties.append(extended_properties)


def extends_index_dynamic_templates(*templates: Dict[str, Any]):
    """
    Add dynamic mapping template configuration to rubrix index template

    See https://www.elastic.co/guide/en/elasticsearch/reference/7.x/dynamic-templates.html#dynamic-templates

    Parameters
    ----------
    templates:
        One or several mapping templates
    """
    _extensions.dynamic_templates.extend(templates)


def extends_index_analyzers(analyzers: Dict[str, Any]):
    """
    Add index analysis configuration to rubrix index template

    See https://www.elastic.co/guide/en/elasticsearch/reference/current/analyzer.html

    Parameters
    ----------
    analyzers:
        The analyzers configuration. Several analyzers could be configured here
    """
    _extensions.analyzers.append(analyzers)


def dataset_records_index(dataset_id: str) -> str:
    """
    Returns dataset records index for a given dataset id

    The dataset info is stored in two elasticsearch indices. The main
    index where all datasets definition are stored and
    an specific dataset index for data records.

    This function calculates the corresponding dataset records index
    for a given dataset id.

    Parameters
    ----------
    dataset_id

    Returns
    -------
        The dataset records index name

    """
    return DATASETS_RECORDS_INDEX_NAME.format(dataset_id)


class DatasetRecordsDAO:
    """Datasets records DAO"""

    _INSTANCE = None

    # Keep info about elasticsearch mappings per task
    # This info must be provided by each task using dao.register_task_mappings method
    _MAPPINGS_BY_TASKS = {}

    __HIGHLIGHT_PRE_TAG__ = "<@@-rb-key>"
    __HIGHLIGHT_POST_TAG__ = "</@@-rb-key>"
    __HIGHLIGHT_VALUES_REGEX__ = re.compile(
        rf"{__HIGHLIGHT_PRE_TAG__}(.+?){__HIGHLIGHT_POST_TAG__}"
    )

    @classmethod
    def get_instance(
        cls,
        es: ElasticsearchWrapper = Depends(ElasticsearchWrapper.get_instance),
    ) -> "DatasetRecordsDAO":
        """
        Creates a dataset records dao instance

        Parameters
        ----------
        es:
            The elasticserach wrapper dependency

        """
        if not cls._INSTANCE:
            cls._INSTANCE = cls(es)
        return cls._INSTANCE

    def __init__(self, es: ElasticsearchWrapper):
        self._es = es
        self.init()

    def init(self):
        """Initializes dataset records dao. Used on app startup"""
        self._es.delete_index_template(index_template=DATASETS_RECORDS_INDEX_NAME)

    def add_records(
        self,
        dataset: BaseDatasetDB,
        records: List[DBRecord],
        record_class: Type[DBRecord],
    ) -> int:
        """
        Add records to dataset

        Parameters
        ----------
        dataset:
            The dataset
        records:
            The list of records
        record_class:
            Record class used to convert records to
        Returns
        -------
            The number of failed records

        """

        now = None
        documents = []
        metadata_values = {}

        if "last_updated" in record_class.schema()["properties"]:
            now = datetime.datetime.utcnow()

        for r in records:
            metadata_values.update(r.metadata or {})
            db_record = record_class.parse_obj(r)
            if now:
                db_record.last_updated = now
            documents.append(
                db_record.dict(exclude_none=False, exclude={"search_keywords"})
            )

        index_name = self.create_dataset_index(dataset)
        self._configure_metadata_fields(index_name, metadata_values)
        return self._es.add_documents(
            index=index_name,
            documents=documents,
            doc_id=lambda _record: _record.get("id"),
        )

    def get_metadata_schema(self, dataset: BaseDatasetDB) -> Dict[str, str]:
        """Get metadata fields schema for provided dataset"""
        records_index = dataset_records_index(dataset.id)
        return self._es.get_field_mapping(index=records_index, field_name="metadata.*")

    def search_records(
        self,
        dataset: BaseDatasetDB,
        search: Optional[RecordSearch] = None,
        size: int = 100,
        record_from: int = 0,
        exclude_fields: List[str] = None,
    ) -> RecordSearchResults:
        """
        SearchRequest records under a dataset given a search parameters.

        Parameters
        ----------
        dataset:
            The dataset
        search:
            The search params
        size:
            Number of records to retrieve (for pagination)
        record_from:
            Record from which to retrieve the records (for pagination)
        exclude_fields:
            a list of fields to exclude from the result source. Wildcards are accepted
        Returns
        -------
            The search result

        """
        search = search or RecordSearch()
        records_index = dataset_records_index(dataset.id)
        compute_aggregations = record_from == 0
        aggregation_requests = (
            {**(search.aggregations or {})} if compute_aggregations else {}
        )

        es_query = {
            "_source": {"excludes": exclude_fields or []},
            "from": record_from,
            "query": search.query or {"match_all": {}},
            "sort": search.sort or [{"_id": {"order": "asc"}}],
            "aggs": aggregation_requests,
            "highlight": self.__configure_query_highlight__(),
        }

        try:
            results = self._es.search(index=records_index, query=es_query, size=size)
        except ClosedIndexError:
            raise ClosedDatasetError(dataset.name)
        except IndexNotFoundError:
            raise MissingDatasetRecordsError(
                f"No records index found for dataset {dataset.name}"
            )

        if compute_aggregations and search.include_default_aggregations:
            current_aggrs = results.get("aggregations", {})
            for aggr in [
                aggregations.predicted_by(),
                aggregations.annotated_by(),
                aggregations.status(),
                aggregations.words_cloud(),
                aggregations.score(),
                aggregations.custom_fields(self.get_metadata_schema(dataset)),
            ]:
                if aggr:
                    aggr_results = self._es.search(
                        index=records_index,
                        query={"query": es_query["query"], "aggs": aggr},
                    )
                    current_aggrs.update(aggr_results["aggregations"])
            results["aggregations"] = current_aggrs

        hits = results["hits"]
        total = hits["total"]
        docs = hits["hits"]
        search_aggregations = results.get("aggregations", {})

        result = RecordSearchResults(
            total=total,
            records=list(map(self.__esdoc2record__, docs)),
        )
        if search_aggregations:
            parsed_aggregations = parse_aggregations(search_aggregations)

            if search.include_default_aggregations:
                parsed_aggregations = unflatten_dict(
                    parsed_aggregations, stop_keys=["metadata"]
                )
                result.words = parsed_aggregations.pop("words", {})
                result.metadata = parsed_aggregations.pop("metadata", {})
            result.aggregations = parsed_aggregations

        return result

    def scan_dataset(
        self,
        dataset: BaseDatasetDB,
        search: Optional[RecordSearch] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Iterates over a dataset records

        Parameters
        ----------
        dataset:
            The dataset
        search:
            The search parameters. Optional

        Returns
        -------
            An iterable over found dataset records
        """
        search = search or RecordSearch()
        es_query = {
            "query": search.query,
            "highlight": self.__configure_query_highlight__(),
        }
        docs = self._es.list_documents(
            dataset_records_index(dataset.id), query=es_query
        )
        for doc in docs:
            yield self.__esdoc2record__(doc)

    def __esdoc2record__(self, doc: Dict[str, Any]):
        return {
            **doc["_source"],
            "id": doc["_id"],
            "search_keywords": self.__parse_highlight_results__(doc),
        }

    @classmethod
    def __parse_highlight_results__(cls, doc: Dict[str, Any]) -> Optional[List[str]]:
        highlight_info = doc.get("highlight")
        if not highlight_info:
            return None

        search_keywords = []
        for content in highlight_info.values():
            if not isinstance(content, list):
                content = [content]
            for text in content:
                search_keywords.extend(re.findall(cls.__HIGHLIGHT_VALUES_REGEX__, text))
        return list(set(search_keywords))

    def _configure_metadata_fields(self, index: str, metadata_values: Dict[str, Any]):
        def check_metadata_length(metadata_length: int = 0):
            if metadata_length > settings.metadata_fields_limit:
                raise MetadataLimitExceededError(
                    length=metadata_length, limit=settings.metadata_fields_limit
                )

        def detect_nested_type(v: Any) -> bool:
            """Returns True if value match as nested value"""
            return isinstance(v, list) and isinstance(v[0], dict)

        check_metadata_length(len(metadata_values))
        check_metadata_length(
            len(
                {
                    *self._es.get_field_mapping(index, "metadata.*"),
                    *[k for k in metadata_values.keys()],
                }
            )
        )
        for field, value in metadata_values.items():
            if detect_nested_type(value):
                self._es.create_field_mapping(
                    index,
                    field_name=f"metadata.{field}",
                    mapping=mappings.nested_field(),
                )

    def register_task_mappings(self, task_type: TaskType, mappings: Dict[str, Any]):
        """
        Register an index mappings configuration for provided task.

        Args:
            task_type:
                The task Type
            mappings:
                The elasticsearch index mappings section configuration
        """
        self._MAPPINGS_BY_TASKS[task_type] = mappings.copy()

    def create_dataset_index(
        self, dataset: BaseDatasetDB, force_recreate: bool = False
    ) -> str:
        """
        Creates a dataset records elasticsearch index based on dataset task type

        Args:
            dataset:
                The dataset
            force_recreate:
                If True, the index will be deleted and recreated

        Returns:
            The generated index name.
        """
        _mappings = tasks_common_mappings()
        task_mappings = self._MAPPINGS_BY_TASKS[dataset.task]
        for k in task_mappings:
            if isinstance(task_mappings[k], list):
                _mappings[k] = [*_mappings.get(k, []), *task_mappings[k]]
            else:
                _mappings[k] = {**_mappings.get(k, {}), **task_mappings[k]}

        index_name = dataset_records_index(dataset.id)
        self._es.create_index(
            index=index_name,
            settings=tasks_common_settings(),
            mappings={**tasks_common_mappings(), **_mappings},
            force_recreate=force_recreate,
        )
        return index_name

    def get_dataset_schema(self, dataset: BaseDatasetDB) -> Dict[str, Any]:
        """Return inner elasticsearch index configuration"""
        index_name = dataset_records_index(dataset.id)
        return self._es.__client__.indices.get_mapping(index=index_name)

    @classmethod
    def __configure_query_highlight__(cls):
        return {
            "pre_tags": [cls.__HIGHLIGHT_PRE_TAG__],
            "post_tags": [cls.__HIGHLIGHT_POST_TAG__],
            "require_field_match": False,
            "fields": {"text": {}},
        }


_instance: Optional[DatasetRecordsDAO] = None


@deprecated.deprecated(reason="Use `DatasetRecordsDAO.get_instance` instead")
def dataset_records_dao(
    es: ElasticsearchWrapper = Depends(create_es_wrapper),
) -> DatasetRecordsDAO:
    """
    Creates a dataset records dao instance

    Parameters
    ----------
    es:
        The elasticserach wrapper dependency

    """
    global _instance
    if not _instance:
        _instance = DatasetRecordsDAO(es)
    return _instance
