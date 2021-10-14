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
from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar

from fastapi import Depends

from rubrix.server.commons.es_wrapper import ElasticsearchWrapper, create_es_wrapper
from rubrix.server.commons.helpers import unflatten_dict
from rubrix.server.datasets.dao import (
    DATASETS_RECORDS_INDEX_NAME,
    dataset_records_index,
)
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.metrics.model import DatasetMetricResults
from rubrix.server.tasks.commons import BaseRecord
from rubrix.server.tasks.commons.dao.model import RecordSearch, RecordSearchResults
from rubrix.server.commons.es_helpers import (
    DATASETS_RECORDS_INDEX_TEMPLATE,
    aggregations,
    parse_aggregations,
)


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


class DatasetRecordsDAO:
    """Datasets records DAO"""

    def __init__(self, es: ElasticsearchWrapper):
        self._es = es
        self.init()

    def init(self):
        """Initializes dataset records dao. Used on app startup"""

        template = DATASETS_RECORDS_INDEX_TEMPLATE.copy()

        if _extensions.analyzers:
            for analyzer in _extensions.analyzers:
                template["settings"]["analysis"]["analyzer"].update(analyzer)

        if _extensions.dynamic_templates:
            for dynamic_template in _extensions.dynamic_templates:
                template["mappings"]["dynamic_templates"].append(dynamic_template)

        if _extensions.properties:
            for property in _extensions.properties:
                template["mappings"]["properties"].update(property)

        self._es.create_index_template(
            name=DATASETS_RECORDS_INDEX_NAME,
            template=template,
            force_recreate=True,
        )

    def add_records(
        self,
        dataset: DatasetDB,
        records: List[BaseRecord],
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
            documents.append(db_record.dict(exclude_none=True))

        index_name = dataset_records_index(dataset.id)

        self._es.create_index(index=index_name)
        self._configure_metadata_fields(index_name, metadata_values)
        return self._es.add_documents(
            index=index_name,
            documents=documents,
            doc_id=lambda _record: _record.get("id"),
        )

    def search_records(
        self,
        dataset: DatasetDB,
        search: Optional[RecordSearch] = None,
        size: int = 100,
        record_from: int = 0,
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
            Record from witch retrieve records (for pagination)
        Returns
        -------
            The search result

        """
        search = search or RecordSearch()
        records_index = dataset_records_index(dataset.id)
        metadata_fields = self._es.get_field_mapping(
            index=records_index, field_name="metadata.*"
        )
        search_aggregations = (
            {
                **(search.aggregations or {}),
                **aggregations.predicted_as(),
                **aggregations.predicted_by(),
                **aggregations.annotated_as(),
                **aggregations.annotated_by(),
                **aggregations.status(),
                **aggregations.predicted(),
                **aggregations.words_cloud(),
                **aggregations.score(),  # TODO: calculate score directly from dataset
                **aggregations.custom_fields(metadata_fields),
            }
            if record_from == 0
            else None
        )

        if record_from > 0:
            search_aggregations = None

        es_query = {
            "size": size,
            "from": record_from,
            "query": search.query or {"match_all": {}},
            "sort": search.sort or [{"_id": {"order": "asc"}}],
            "aggs": search_aggregations or {},
        }
        results = self._es.search(index=records_index, query=es_query, size=size)

        hits = results["hits"]
        total = hits["total"]
        docs = hits["hits"]
        search_aggregations = results.get("aggregations", {})

        result = RecordSearchResults(
            total=total,
            records=[doc["_source"] for doc in docs],
        )
        if search_aggregations:
            parsed_aggregations = parse_aggregations(search_aggregations)
            parsed_aggregations = unflatten_dict(
                parsed_aggregations, stop_keys=["metadata"]
            )

            result.words = parsed_aggregations.pop("words")
            result.metadata = parsed_aggregations.pop("metadata", {})

            metrics_results = [
                DatasetMetricResults(
                    id=metric.id,
                    name=metric.name,
                    description=metric.description,
                    kind=metric.spec.get("meta", {"kind": "custom"})["kind"],
                    results=parsed_aggregations.pop(metric.id),
                )
                for metric in dataset.metrics
                if metric.id in parsed_aggregations
            ]
            result.metrics = metrics_results
            result.aggregations = parsed_aggregations
        return result

    def scan_dataset(
        self,
        dataset: DatasetDB,
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
        }
        docs = self._es.list_documents(
            dataset_records_index(dataset.id), query=es_query
        )
        for doc in docs:
            yield doc["_source"]

    def _configure_metadata_fields(self, index: str, metadata_values: Dict[str, Any]):
        def detect_nested_type(v: Any) -> bool:
            """Returns True if value match as nested value"""
            return isinstance(v, list) and isinstance(v[0], dict)

        for field, value in metadata_values.items():
            if detect_nested_type(value):
                self._es.create_field_mapping(
                    index, field_name=f"metadata.{field}", type="nested"
                )


_instance: Optional[DatasetRecordsDAO] = None


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
