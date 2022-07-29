import logging
from enum import Enum
from typing import Any, Dict, Optional, TypeVar

from luqum.elasticsearch import ElasticsearchQueryBuilder, SchemaAnalyzer
from luqum.parser import parser

from rubrix.server.elasticseach.query_helpers import filters
from rubrix.server.elasticseach.search.model import (
    AbstractQuery,
    BaseSearchQuery,
    DatasetsQuery,
)
from rubrix.server.services.search.model import QueryRange

SearchQuery = TypeVar("SearchQuery", bound=BaseSearchQuery)
Query = TypeVar("Query", bound=AbstractQuery)


class EsQueryBuilder:
    _INSTANCE: "EsQueryBuilder" = None
    _LOGGER = logging.getLogger(__name__)

    @classmethod
    def get_instance(cls):
        if not cls._INSTANCE:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def _datasets_to_es_query(
        self, query: Optional[DatasetsQuery] = None
    ) -> Dict[str, Any]:
        if not query:
            return filters.match_all()

        query_filters = []
        if query.owners:
            owners_filter = filters.terms_filter("owner.keyword", query.owners)
            if query.include_no_owner:
                query_filters.append(
                    filters.boolean_filter(
                        minimum_should_match=1,  # OR Condition
                        should_filters=[
                            owners_filter,
                            filters.boolean_filter(
                                must_not_query=filters.exists_field("owner")
                            ),
                        ],
                    )
                )
            else:
                query_filters.append(owners_filter)

        if query.tasks:
            query_filters.append(
                filters.terms_filter(field="task.keyword", values=query.tasks)
            )

        if not query_filters:
            return filters.match_all()
        return filters.boolean_filter(
            should_filters=query_filters, minimum_should_match=len(query_filters)
        )

    def _search_to_es_query(
        self,
        schema: Optional[Dict[str, Any]] = None,
        query: Optional[SearchQuery] = None,
    ):
        if not query:
            return filters.match_all()

        if not query.advanced_query_dsl or not query.query_text:
            return self._to_es_query(query)

        text_search = query.query_text
        new_query = query.copy(update={"query_text": None})

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
            filter_query=self._to_es_query(new_query), must_query=query_text
        )

    def __call__(
        self,
        schema: Optional[Dict[str, Any]] = None,
        query: Optional[Query] = None,
    ) -> Dict[str, Any]:

        if isinstance(query, DatasetsQuery):
            return self._datasets_to_es_query(query)
        return self._search_to_es_query(schema, query)

    @classmethod
    def _to_es_query(cls, query: SearchQuery) -> Dict[str, Any]:
        if query.ids:
            return filters.ids_filter(query.ids)

        query_text = filters.text_query(query.query_text)
        all_filters = filters.metadata(query.metadata)
        if query.has_annotation:
            all_filters.append(filters.exists_field("annotated_by"))
        if query.has_prediction:
            all_filters.append(filters.exists_field("predicted_by"))

        query_data = query.dict(
            exclude={
                "advanced_query_dsl",
                "query_text",
                "metadata",
                "uncovered_by_rules",
                "has_annotation",
                "has_prediction",
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
