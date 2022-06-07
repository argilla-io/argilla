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

from rubrix.server._helpers import unflatten_dict
from rubrix.server.apis.v0.models.commons.model import BaseRecord, TaskType
from rubrix.server.apis.v0.models.datasets import BaseDatasetDB
from rubrix.server.apis.v0.settings.server import settings
from rubrix.server.daos.models.records import RecordSearch, RecordSearchResults
from rubrix.server.elasticseach.client_wrapper import (
    ClosedIndexError,
    ElasticsearchWrapper,
    IndexNotFoundError,
    create_es_wrapper,
)
from rubrix.server.elasticseach.mappings.datasets import DATASETS_RECORDS_INDEX_NAME
from rubrix.server.elasticseach.mappings.helpers import (
    mappings,
    tasks_common_mappings,
    tasks_common_settings,
)
from rubrix.server.elasticseach.query_helpers import aggregations, parse_aggregations
from rubrix.server.errors import ClosedDatasetError, MissingDatasetRecordsError
from rubrix.server.errors.task_errors import MetadataLimitExceededError

DBRecord = TypeVar("DBRecord", bound=BaseRecord)


@dataclasses.dataclass
class _IndexTemplateExtensions:

    analyzers: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    properties: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    dynamic_templates: List[Dict[str, Any]] = dataclasses.field(default_factory=list)


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

    __HIGHLIGHT_PHRASE_PRE_PARSER_REGEX__ = re.compile(
        rf"{__HIGHLIGHT_POST_TAG__}\s+{__HIGHLIGHT_PRE_TAG__}"
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
        pass

    def add_records(
        self,
        dataset: BaseDatasetDB,
        mappings: Dict[str, Any],
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

        index_name = self.create_dataset_index(dataset, mappings=mappings)
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
        highligth_results: bool = True,
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

        sort_config = self.__normalize_sort_config__(records_index, sort=search.sort)

        es_query = {
            "_source": {"excludes": exclude_fields or []},
            "from": record_from,
            "query": search.query or {"match_all": {}},
            "sort": sort_config,
            "aggs": aggregation_requests,
        }
        if highligth_results:
            es_query["highlight"] = self.__configure_query_highlight__(
                task=dataset.task
            )

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
                aggregations.predicted(),
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

    def __normalize_sort_config__(
        self, index: str, sort: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        id_field = "id"
        id_keyword_field = "id.keyword"
        sort_config = []

        for sort_field in sort or [{id_field: {"order": "asc"}}]:
            for field in sort_field:
                if field == id_field and self._es.get_field_mapping(
                    index=index, field_name=id_keyword_field
                ):
                    sort_config.append({id_keyword_field: sort_field[field]})
                else:
                    sort_config.append(sort_field)
        return sort_config

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
            "query": search.query or {"match_all": {}},
            "highlight": self.__configure_query_highlight__(task=dataset.task),
        }
        docs = self._es.list_documents(
            dataset_records_index(dataset.id), query=es_query
        )
        for doc in docs:
            yield self.__esdoc2record__(doc)

    def __esdoc2record__(
        self,
        doc: Dict[str, Any],
        query: Optional[str] = None,
        is_phrase_query: bool = True,
    ):
        return {
            **doc["_source"],
            "id": doc["_id"],
            "search_keywords": self.__parse_highlight_results__(
                doc, query=query, is_phrase_query=is_phrase_query
            ),
        }

    @classmethod
    def __parse_highlight_results__(
        cls,
        doc: Dict[str, Any],
        query: Optional[str] = None,
        is_phrase_query: bool = False,
    ) -> Optional[List[str]]:
        highlight_info = doc.get("highlight")
        if not highlight_info:
            return None

        search_keywords = []
        for content in highlight_info.values():
            if not isinstance(content, list):
                content = [content]
            text = " ".join(content)

            if is_phrase_query:
                text = re.sub(cls.__HIGHLIGHT_PHRASE_PRE_PARSER_REGEX__, " ", text)
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

    def create_dataset_index(
        self,
        dataset: BaseDatasetDB,
        mappings: Dict[str, Any],
        force_recreate: bool = False,
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
        task_mappings = mappings.copy()
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
        response = self._es.__client__.indices.get_mapping(index=index_name)

        if index_name in response:
            response = response.get(index_name)

        return response

    @classmethod
    def __configure_query_highlight__(cls, task: TaskType):

        return {
            "pre_tags": [cls.__HIGHLIGHT_PRE_TAG__],
            "post_tags": [cls.__HIGHLIGHT_POST_TAG__],
            "require_field_match": True,
            "fields": {
                "text": {},
                "text.*": {},
                # TODO(@frascuchon): `words` will be removed in version 0.16.0
                "words": {},
                **({"inputs.*": {}} if task == TaskType.text_classification else {}),
            },
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
