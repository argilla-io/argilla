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

        if not query.advanced_query_dsl or not query.query_text:
            return query.as_elasticsearch()

        text_search = query.query_text
        query.query_text = None

        schema = self.__dao__.get_dataset_schema(dataset)
        schema = SchemaAnalyzer(schema)
        es_query_builder = ElasticsearchQueryBuilder(
            **{
                **schema.query_builder_options(),
                "default_field": "words",
            }  # TODO: This will change
        )

        query_tree = parser.parse(text_search)
        query_text = es_query_builder(query_tree)

        return es_helpers.filters.boolean_filter(
            filter_query=query.as_elasticsearch(), must_query=query_text
        )
