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

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from luqum.elasticsearch import ElasticsearchQueryBuilder, SchemaAnalyzer
from luqum.parser import parser

from argilla.server.daos.backend.query_helpers import filters
from argilla.server.daos.backend.search.model import (
    BackendDatasetsQuery,
    BackendQuery,
    BackendRecordsQuery,
    BaseDatasetsQuery,
    QueryRange,
    SortableField,
    SortConfig,
)


class EsQueryBuilder:
    _INSTANCE: "EsQueryBuilder" = None
    _LOGGER = logging.getLogger(__name__)

    @classmethod
    def get_instance(cls):
        if not cls._INSTANCE:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def _datasets_to_es_query(
        self, query: Optional[BackendDatasetsQuery] = None
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
        if query.name:
            query_filters.append(
                filters.term_filter(field="name.keyword", value=query.name)
            )
        if not query_filters:
            return filters.match_all()
        return filters.boolean_filter(
            should_filters=query_filters, minimum_should_match=len(query_filters)
        )

    def _search_to_es_query(
        self,
        schema: Optional[Dict[str, Any]] = None,
        query: Optional[BackendRecordsQuery] = None,
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
            }
        )

        query_tree = parser.parse(text_search)
        query_text = es_query_builder(query_tree)

        return filters.boolean_filter(
            filter_query=self._to_es_query(new_query), must_query=query_text
        )

    def map_2_es_query(
        self,
        schema: Optional[Dict[str, Any]] = None,
        query: Optional[BackendQuery] = None,
        sort: Optional[SortConfig] = None,
        id_from: Optional[str] = None,
    ) -> Dict[str, Any]:
        es_query: Dict[str, Any] = (
            {"query": self._datasets_to_es_query(query)}
            if isinstance(query, BaseDatasetsQuery)
            else {"query": self._search_to_es_query(schema, query)}
        )

        if id_from:
            es_query["search_after"] = [id_from]
            sort = SortConfig()  # sort by id as default

        es_sort = self.map_2_es_sort_configuration(schema=schema, sort=sort)
        if es_sort:
            es_query["sort"] = es_sort

        return es_query

    def map_2_es_sort_configuration(
        self, schema: Optional[Dict[str, Any]] = None, sort: Optional[SortConfig] = None
    ) -> Optional[List[Dict[str, Any]]]:

        if not sort:
            return None

        # TODO(@frascuchon): compute valid list from the schema
        valid_fields = sort.valid_fields or [
            "id",
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

        id_field = "id"
        id_keyword_field = "id.keyword"
        schema = schema or {}
        mappings = self._clean_mappings(schema.get("mappings", {}))
        use_id_keyword = "text" == mappings.get("id")

        es_sort = []
        for sortable_field in sort.sort_by or [SortableField(id="id")]:
            if valid_fields:
                if not sortable_field.id.split(".")[0] in valid_fields:
                    raise AssertionError(
                        f"Wrong sort id {sortable_field.id}. Valid values are: "
                        f"{[str(v) for v in valid_fields]}"
                    )
            field = sortable_field.id
            if field == id_field and use_id_keyword:
                field = id_keyword_field
            es_sort.append({field: {"order": sortable_field.order}})

        return es_sort

    @classmethod
    def _to_es_query(cls, query: BackendRecordsQuery) -> Dict[str, Any]:
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
