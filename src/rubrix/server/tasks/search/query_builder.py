from typing import Any, Dict, TypeVar

from fastapi import Depends
from luqum.elasticsearch import ElasticsearchQueryBuilder, SchemaAnalyzer
from luqum.parser import parser

from rubrix.server.commons import es_helpers
from rubrix.server.datasets.model import BaseDatasetDB, Dataset
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO
from rubrix.server.tasks.search.model import BaseSearchQuery

SearchQuery = TypeVar("SearchQuery", bound=BaseSearchQuery)


class EsQueryBuilder:
    _INSTANCE: "EsQueryBuilder" = None

    @classmethod
    def get_instance(
        cls, dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance)
    ):
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao=dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetRecordsDAO):
        self.__dao__ = dao

    def __call__(self, dataset: BaseDatasetDB, query: SearchQuery) -> Dict[str, Any]:

        if not query.advanced_query_dsl or not query.query_text:
            return query.as_elasticsearch()

        text_search = query.query_text
        new_query = query.copy(update={"query_text": None})

        schema = self.__dao__.get_dataset_schema(dataset)
        schema = SchemaAnalyzer(schema)
        es_query_builder = ElasticsearchQueryBuilder(
            **{
                **schema.query_builder_options(),
                "default_field": "text",
            }  # TODO: This will change
        )

        query_tree = parser.parse(text_search)
        query_text = es_query_builder(query_tree)

        return es_helpers.filters.boolean_filter(
            filter_query=new_query.as_elasticsearch(), must_query=query_text
        )
