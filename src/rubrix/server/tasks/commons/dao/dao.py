from typing import Any, Dict, Iterable, List, Optional

from fastapi import Depends
from rubrix.server.commons.es_wrapper import ElasticsearchWrapper, create_es_wrapper
from rubrix.server.commons.helpers import unflatten_dict
from rubrix.server.datasets.dao import (
    DATASETS_RECORDS_INDEX_NAME,
    dataset_records_index,
)
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.tasks.commons.dao.model import RecordSearch, RecordSearchResults
from rubrix.server.tasks.commons.es_helpers import (
    DATASETS_RECORDS_INDEX_TEMPLATE,
    aggregations,
    parse_aggregations,
)


class DatasetRecordsDAO:
    """Datasets records DAO"""

    def __init__(self, es: ElasticsearchWrapper):
        self._es = es
        self.init()

    def init(self):
        """Initializes dataset records dao. Used on app startup"""
        self._es.create_index_template(
            name=DATASETS_RECORDS_INDEX_NAME,
            template=DATASETS_RECORDS_INDEX_TEMPLATE,
            force_recreate=True,
        )

    def add_records(
        self,
        dataset: DatasetDB,
        records: List[Dict[str, Any]],
    ) -> int:
        """
        Add records to dataset

        Parameters
        ----------
        dataset:
            The dataset
        records:
            The list of records

        Returns
        -------
            The number of failed records

        """
        return self._es.add_documents(
            index=dataset_records_index(dataset.id),
            documents=records,
            doc_id=lambda r: r.get("id"),
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
            "sort": [{"_id": {"order": "asc"}}],  # TODO: Sort by event timestamp?
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
