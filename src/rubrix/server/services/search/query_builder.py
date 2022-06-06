import logging
from enum import Enum
from typing import Any, Dict, Optional, TypeVar

from fastapi import Depends
from luqum.elasticsearch import ElasticsearchQueryBuilder, SchemaAnalyzer
from luqum.parser import parser

from rubrix.server.apis.v0.models.commons.model import QueryRange
from rubrix.server.apis.v0.models.datasets import BaseDatasetDB
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.elasticseach.query_helpers import filters
from rubrix.server.services.search.model import BaseSearchQuery

SearchQuery = TypeVar("SearchQuery", bound=BaseSearchQuery)


class EsQueryBuilder:
    _INSTANCE: "EsQueryBuilder" = None
    _LOGGER = logging.getLogger(__name__)

    @classmethod
    def get_instance(
        cls, dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance)
    ):
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao=dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetRecordsDAO):
        self.__dao__ = dao

    def __call__(
        self, dataset: BaseDatasetDB, query: Optional[SearchQuery] = None
    ) -> Dict[str, Any]:

        if not query:
            return filters.match_all()

        if not query.advanced_query_dsl or not query.query_text:
            return self.to_es_query(query)

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

        return filters.boolean_filter(
            filter_query=self.to_es_query(new_query), must_query=query_text
        )

    @classmethod
    def to_es_query(cls, query: BaseSearchQuery) -> Dict[str, Any]:
        if query.ids:
            return filters.ids_filter(query.ids)

        query_text = filters.text_query(query.query_text)
        all_filters = filters.metadata(query.metadata)
        query_data = query.dict(
            exclude={
                "advanced_query_dsl",
                "query_text",
                "metadata",
                "uncovered_by_rules",
            }
        )
        for key, value in query_data.items():
            if value is None:
                continue
            key_filter = None
            if isinstance(value, dict):
                value = getattr(query, key)  # check the original field type
            if isinstance(value, list):
                key_filter = filters.terms_filter(key, value)
            elif isinstance(value, (str, Enum)):
                key_filter = filters.term_filter(key, value)
            elif isinstance(value, QueryRange):
                key_filter = filters.range_filter(
                    field=key, value_from=value.range_from, value_to=value.range_to
                )
            else:
                cls._LOGGER.warning(f"Cannot parse query value {value} for key {key}")

            if key_filter:
                all_filters.append(key_filter)

        return filters.boolean_filter(
            must_query=query_text or filters.match_all(),
            filter_query=filters.boolean_filter(
                should_filters=all_filters, minimum_should_match=len(all_filters)
            )
            if all_filters
            else None,
            must_not_query=filters.boolean_filter(
                should_filters=[filters.text_query(q) for q in query.uncovered_by_rules]
            )
            if hasattr(query, "uncovered_by_rules") and query.uncovered_by_rules
            else None,
        )
