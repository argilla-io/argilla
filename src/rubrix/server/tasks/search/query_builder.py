from typing import Any, Dict, TypeVar

from luqum.elasticsearch import ElasticsearchQueryBuilder, SchemaAnalyzer
from luqum.parser import parser

from rubrix.server.commons import es_helpers
from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO
from rubrix.server.tasks.search.model import BaseSearchQuery

SearchQuery = TypeVar("SearchQuery", bound=BaseSearchQuery)


class EsQueryBuilder:
    def __init__(self, dao: DatasetRecordsDAO):
        self.__dao__ = dao

    def __call__(self, dataset: Dataset, query: SearchQuery) -> Dict[str, Any]:
        text_search = query.query_text
        query.query_text = ""

        if query.advanced_query_dsl:
            schema = self.__dao__.get_dataset_schema(dataset)
            schema = SchemaAnalyzer(schema)
            es_query_builder = ElasticsearchQueryBuilder(
                **schema.query_builder_options()
            )

            query_tree = parser.parse(query.query_text)
            query_text = es_query_builder(query_tree)
        else:
            query_text = es_helpers.filters.text_query(text_search)

        return es_helpers.filters.boolean_filter(
            should_filters=[query_text, query.as_elasticsearch()],
            minimum_should_match=2,
        )
