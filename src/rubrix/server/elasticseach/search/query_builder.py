import logging
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar

from luqum.elasticsearch import ElasticsearchQueryBuilder, SchemaAnalyzer
from luqum.parser import parser

from rubrix.server.elasticseach.query_helpers import filters
from rubrix.server.elasticseach.search.model import (
    AbstractQuery,
    BaseSearchQuery,
    DatasetsQuery,
    SortConfig,
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
        sort: Optional[SortConfig] = None,
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

    def map_2_es_query(
        self,
        schema: Optional[Dict[str, Any]] = None,
        query: Optional[Query] = None,
        sort: Optional[SortConfig] = None,
    ) -> Dict[str, Any]:
        es_query: Dict[str, Any] = (
            {"query": self._datasets_to_es_query(query)}
            if isinstance(query, DatasetsQuery)
            else {"query": self._search_to_es_query(schema, query)}
        )
        es_sort = self.map_2_es_sort_configuration(sort, schema=schema)
        if es_sort:
            es_query["sort"] = es_sort
        return es_query

    def map_2_es_sort_configuration(
        self, sort: Optional[SortConfig] = None, schema: Dict[str, Any] = None
    ) -> Optional[List[Dict[str, Any]]]:

        if not sort:
            return None

        valid_fields = sort.valid_fields or [
            "metadata",
            "score",
            "predicted",
            "predicted_as",
            "predicted_by",
            "annotated_as",
            "annotated_by",
            "status",
            "last_updated",
            "event_timestamp",
        ]
        result = []
        id_field = "id"
        id_keyword_field = "id.keyword"
        sort_config = []

        for sortable_field in sort.sort_by:
            if valid_fields:
                if not sortable_field.id.split(".")[0] in valid_fields:
                    raise AssertionError(
                        f"Wrong sort id {sortable_field.id}. Valid values are: "
                        f"{[str(v) for v in valid_fields]}"
                    )
            result.append({sortable_field.id: {"order": sortable_field.order}})

        mappings = self._clean_mappings(schema["mappings"])
        for sort_field in result or [{id_field: {"order": "asc"}}]:
            for field in sort_field:
                if field == id_field and mappings.get(id_keyword_field):
                    sort_config.append({id_keyword_field: sort_field[field]})
                else:
                    sort_config.append(sort_field)

        return sort_config

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

    def _clean_mappings(self, mappings: Dict[str, Any]):
        if not mappings:
            return {}

        return {
            key: definition.get("type") or self._clean_mappings(definition)
            for key, definition in mappings["properties"].items()
        }
